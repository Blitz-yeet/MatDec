from core.calc_beam import check_beam_safety

def main():
    span = 12.0
    w = 15.0
    profile = "IPE 750 x 220"
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

if __name__ == "__main__":
    main()
