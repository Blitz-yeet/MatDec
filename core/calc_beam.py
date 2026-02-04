# core/calc_beam.py


"""
Beam calculation functions for Version 1.

I assume that the beam is simply supported, with a uniformly distributed load, and that we are using a steel IPE section. 
The behavior is linear elastic and we check both strength and deflection criteria. 

All units inside the calculations:
- Length: m
- Load: N/m  (we convert from kN/m)
- E (Young's modulus): Pa (N/m2)
- I: m4
- W: m3
- Stress: Pa
"""

# Import section properties
from .sections import get_section


# Material properties and safety factors
E_STEEL = 210e9   # Young's modulus of steel [Pa]
GAMMA_M = 1.0     # material partial factor (simplified, V1)

# Yield strengths for a few steel grades [Pa]
STEEL_GRADES = {
    "S235": 235e6,
    "S275": 275e6,
    "S355": 355e6,
}


def max_bending_moment_uniform(span_m: float, w_kN_per_m: float) -> float:
    """
    Maximum bending moment for a simply supported beam under uniform load.

    Formula: M = w * L^2 / 8

    Parameters:
        span_m (float): L span in meters
        w_kN_per_m (float): uniform load in kN/m

    It returns the float M_Ed in [Nm]
    """
    w_N_per_m = w_kN_per_m * 1e3  # kN/m → N/m
    M_ed = w_N_per_m * span_m**2 / 8.0
    return M_ed


def bending_resistance_MRd(W_m3: float, fy_Pa: float) -> float:
    """
    Bending resistance M_Rd = W * fy / GAMMA_M

    Parameters:
        W_m3 (float): section modulus [m3]
        fy_Pa (float): yield strength [Pa]

    It returns the float  M_Rd in [Nm]
    """
    M_rd = W_m3 * fy_Pa / GAMMA_M
    return M_rd


def max_deflection_uniform(span_m: float, w_kN_per_m: float, I_m4: float) -> float:
    """
    Maximum deflection for a simply supported beam with uniform load.

    Formula: delta = 5 * w * L^4 / (384 * E * I)

    Parameters:
        span_m (float): span L in meters
        w_kN_per_m (float): uniform load in kN/m
        I_m4 (float): second moment of area [m4]

    It returns the float deflection delta in [m]
    """
    w_N_per_m = w_kN_per_m * 1e3  # kN/m → N/m
    delta = 5 * w_N_per_m * span_m**4 / (384 * E_STEEL * I_m4)
    return delta


def deflection_limit(span_m: float, ratio: float = 250.0) -> float:
    """
    Simple deflection limit: delta_allow = L / ratio

    Parameters:
        span_m (float): span in meters
        ratio (float): for example 250 means L/250

    It returns the float allowable deflection in [m]
    """
    return span_m / ratio


def check_beam_safety(
    span_m: float,
    w_kN_per_m: float,
    profile_name: str,
    steel_grade: str,
) -> dict:
    """
    checks beam safety and deflection for one IPE section.

    Inputs:
        span_m:       span [m]
        w_kN_per_m:   uniform load [kN/m]
        profile_name: e.g. "IPE 300", must exist in materials.csv
        steel_grade:  "S235", "S275", or "S355"

    It returns the dict with internal forces, resistances, deflections, utilizations, and safety flag.
    """

    # 1) Get section properties from your CSV via sections.py
    sec = get_section(profile_name)
    W_m3 = sec["W"]
    I_m4 = sec["I"]

    # 2) Get yield strength for the chosen steel grade
    if steel_grade not in STEEL_GRADES:
        raise ValueError(f"Unknown steel grade: {steel_grade}")
    fy = STEEL_GRADES[steel_grade]

    # 3) Calculate bending moment demand
    M_Ed = max_bending_moment_uniform(span_m, w_kN_per_m)

    # 4) Calculate bending resistance
    M_Rd = bending_resistance_MRd(W_m3, fy)

    # 5) Strength utilization
    util_strength = M_Ed / M_Rd

    # 6) Deflection and limit
    delta = max_deflection_uniform(span_m, w_kN_per_m, I_m4)
    delta_allow = deflection_limit(span_m)
    util_deflection = delta / delta_allow

    # 7) Overall utilization
    util_total = max(util_strength, util_deflection)
    is_safe = util_total <= 1.0

    return {
        "span_m": span_m,
        "w_kN_per_m": w_kN_per_m,
        "profile": profile_name,
        "steel_grade": steel_grade,
        "M_Ed_Nm": M_Ed,
        "M_Rd_Nm": M_Rd,
        "util_strength": util_strength,
        "delta_m": delta,
        "delta_allow_m": delta_allow,
        "util_deflection": util_deflection,
        "util_total": util_total,
        "is_safe": is_safe,
    }


if __name__ == "__main__":
    # Small test so we can run: calc_beam.py
    span = 12.0
    w = 15.0  # kN/m (example)
    profile = "IPE 750 x 220"  # must exist in 12your CSV
    grade = "S355"

    result = check_beam_safety(span, w, profile, grade)

    print("Beam check:")
    print(f"  span           = {result['span_m']} m")
    print(f"  load           = {result['w_kN_per_m']} kN/m")
    print(f"  profile        = {result['profile']}")
    print(f"  steel_grade    = {result['steel_grade']}")
    print()
    print(f"  M_Ed           = {result['M_Ed_Nm']:.2e} Nm")
    print(f"  M_Rd           = {result['M_Rd_Nm']:.2e} Nm")
    print(f"  util_strength  = {result['util_strength']:.2f}")
    print()
    print(f"  delta          = {result['delta_m']:.4f} m")
    print(f"  delta_allow    = {result['delta_allow_m']:.4f} m")
    print(f"  util_deflect   = {result['util_deflection']:.2f}")
    print()
    print(f"  util_total     = {result['util_total']:.2f}")
    print(f"  SAFE?          = {result['is_safe']}")
