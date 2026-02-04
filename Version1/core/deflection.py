# core/deflection.py

E_STEEL_MPA = 210_000.0  # Young's modulus of steel [MPa = N/mm^2]


def max_deflection_simply_supported(
    span_m: float,
    I_cm4: float,
    q_kN_per_m: float = 0.0,
    P_kN: float = 0.0,
) -> float:
    """
    Maximum deflection for a simply supported beam [mm].

    Supports:
    - UDL over full span (q_kN_per_m)
    - Single point load at midspan (P_kN)

    Uses superposition.

    Returns:
        w_max_mm
    """
    # Unit conversions
    L_mm = span_m * 1000.0
    I_mm4 = I_cm4 * 1e4        # cm^4 -> mm^4
    q_N_per_mm = q_kN_per_m    # kN/m == N/mm
    P_N = P_kN * 1000.0        # kN -> N

    w_q = 0.0
    w_P = 0.0

    # Deflection from UDL
    if q_kN_per_m != 0.0:
        w_q = (5 * q_N_per_mm * L_mm**4) / (384 * E_STEEL_MPA * I_mm4)

    # Deflection from midspan point load
    if P_kN != 0.0:
        w_P = (P_N * L_mm**3) / (48 * E_STEEL_MPA * I_mm4)

    return w_q + w_P
