# core/loads.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Iterable, Tuple
import numpy as np


@dataclass
class PointLoad:
    """
    Concentrated load acting on the beam.
    value_kN: negative for downward (usual sign convention).
    position_m: distance from the left support.
    """
    value_kN: float
    position_m: float


@dataclass
class UDL:
    """
    Uniformly distributed load between start_m and end_m.
    intensity_kN_per_m: negative for downward.
    """
    intensity_kN_per_m: float
    start_m: float
    end_m: float


@dataclass
class LoadCase:
    """
    A single load case (e.g. G, Q1, Q2) with partial factor gamma.
    """
    name: str
    span_m: float
    point_loads: List[PointLoad] = field(default_factory=list)
    udls: List[UDL] = field(default_factory=list)
    gamma: float = 1.0  # EC load factor


def combine_load_cases(
    cases: Iterable[LoadCase],
    combination_factors: dict[str, float],
    name: str = "combination",
) -> LoadCase:
    """
    Linear combination of load cases:
    combination_factors = {"G": 1.35, "Q1": 1.5, ...}

    Returns a new LoadCase with combined loads.
    Assumes all cases have the same span.
    """
    cases = list(cases)
    if not cases:
        raise ValueError("No load cases provided.")

    span = cases[0].span_m
    if any(abs(c.span_m - span) > 1e-6 for c in cases):
        raise ValueError("All load cases must have the same span.")

    combined_point_loads: list[PointLoad] = []
    combined_udls: list[UDL] = []

    for lc in cases:
        psi = combination_factors.get(lc.name, 0.0)
        if psi == 0.0:
            continue

        factor = psi * lc.gamma

        for pl in lc.point_loads:
            combined_point_loads.append(
                PointLoad(
                    value_kN=pl.value_kN * factor,
                    position_m=pl.position_m,
                )
            )

        for w in lc.udls:
            combined_udls.append(
                UDL(
                    intensity_kN_per_m=w.intensity_kN_per_m * factor,
                    start_m=w.start_m,
                    end_m=w.end_m,
                )
            )

    return LoadCase(
        name=name,
        span_m=span,
        point_loads=combined_point_loads,
        udls=combined_udls,
        gamma=1.0,
    )


def _reactions_simply_supported(lc: LoadCase) -> Tuple[float, float]:
    """
    Statics for a simply supported beam:
    Returns (RA_kN, RB_kN) = reactions at left and right supports.
    Sign convention: upward positive.
    """
    L = lc.span_m
    RA = 0.0
    RB = 0.0

    # Point loads
    for pl in lc.point_loads:
        P = pl.value_kN
        a = pl.position_m  # from left
        # Total vertical equilibrium + moments about left:
        # For a downward load (negative P), RA and RB should be positive.
        RB += -P * a / L
        RA += -P - (-P * a / L)

    # UDLs
    for w in lc.udls:
        w_int = w.intensity_kN_per_m
        a = w.start_m
        b = w.end_m
        Lw = b - a
        W = w_int * Lw  # total load (kN)
        x_res = a + Lw / 2.0  # resultant location
        RB += -W * x_res / L
        RA += -W - (-W * x_res / L)

    return RA, RB


def analyze_simply_supported(
    lc: LoadCase,
    n_points: int = 201,
) -> dict[str, np.ndarray]:
    """
    Compute shear V(x) and bending moment M(x) for a simply supported beam.

    Returns dict with:
        x_m       : positions along span [m]
        V_kN      : shear force [kN]
        M_kNm     : bending moment [kNm]
        V_max_kN  : max |V|
        M_max_kNm : max |M|
    """
    L = lc.span_m
    x = np.linspace(0.0, L, n_points)

    RA, RB = _reactions_simply_supported(lc)

    V = np.zeros_like(x)
    M = np.zeros_like(x)

    # Add reactions (upward)
    V += RA
    M += RA * x

    V += RB * 0.0  # RB acts at x=L, accounted via point load term below

    # Point loads (downward)
    for pl in lc.point_loads:
        P = pl.value_kN
        a = pl.position_m
        mask = x >= a
        V[mask] += P  # P is negative if downward
        M[mask] += P * (x[mask] - a)

    # UDLs (downward)
    # For each segment [a,b], intensity w
    for w in lc.udls:
        w_int = w.intensity_kN_per_m
        a = w.start_m
        b = w.end_m

        # Three regions: x<a, a<=x<=b, x>b
        mask1 = x >= a
        mask2 = x >= b

        # Region a <= x <= b: part of the UDL active up to x
        x1 = x[mask1]
        length_active = np.clip(x1 - a, 0.0, b - a)
        V[mask1] += w_int * length_active
        M[mask1] += w_int * 0.5 * length_active**2

        # Region x > b: entire UDL is active
        x2 = x[mask2]
        Lw = b - a
        V[mask2] += w_int * (Lw - length_active[mask2[mask1]])  # adjust overlap
        # Simpler (and safer): recompute for x>b exactly
        # but to keep it straightforward, we can handle separately:

    # The simple way: recompute UDL effects cleanly
    V = np.zeros_like(x)
    M = np.zeros_like(x)

    # Re-apply reactions
    V += RA
    M += RA * x

    # Point loads again
    for pl in lc.point_loads:
        P = pl.value_kN
        a = pl.position_m
        mask = x >= a
        V[mask] += P
        M[mask] += P * (x[mask] - a)

    # UDLs again (clean, piecewise)
    for w in lc.udls:
        w_int = w.intensity_kN_per_m
        a = w.start_m
        b = w.end_m
        Lw = b - a

        # For each x, we integrate w over the part of [a,b] that lies ≤ x.
        for i, xi in enumerate(x):
            if xi <= a:
                continue
            elif a < xi <= b:
                l = xi - a
            else:  # xi > b
                l = Lw

            V[i] += w_int * l
            M[i] += w_int * 0.5 * l**2

    # Now add RB as a point reaction at x=L (upward)
    mask_RB = x >= L
    V[mask_RB] += RB
    M[mask_RB] += RB * (x[mask_RB] - L)

    return {
        "x_m": x,
        "V_kN": V,
        "M_kNm": M,
        "V_max_kN": float(np.max(np.abs(V))),
        "M_max_kNm": float(np.max(np.abs(M))),
        "RA_kN": RA,
        "RB_kN": RB,
    }
