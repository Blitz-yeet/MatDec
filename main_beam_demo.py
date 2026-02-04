# main_beam_demo.py

from core.loads import LoadCase, UDL, PointLoad, analyze_simply_supported
from core.co2_calc import MaterialsDB, BeamSelection
from core.deflection import max_deflection_simply_supported


def main():
   
    # Problem definition

    span = 6.0  # beam span [m]

    # Design loads (ULS for bending)
    # NOTE: already factored for simplicity (V1 assumption)
    q_ULS = 15.0   # kN/m (downwards)
    P_ULS = 30.0   # kN at midspan (downwards)

    # Service loads (SLS for deflection)
    # Usually unfactored or reduced
    q_SLS = 15.0   # kN/m
    P_SLS = 30.0   # kN

 
    # Structural analysis (ULS)

    lc = LoadCase(
        name="ULS",
        span_m=span,
        udls=[UDL(intensity_kN_per_m=-q_ULS, start_m=0.0, end_m=span)],
        point_loads=[PointLoad(value_kN=-P_ULS, position_m=span / 2)],
        gamma=1.0,
    )

    res = analyze_simply_supported(lc)
    M_Ed = res["M_max_kNm"]

    print("=== Structural analysis (ULS) ===")
    print(f"Span L       = {span:.2f} m")
    print(f"M_Ed,max     = {M_Ed:.2f} kNm")
    print(f"RA           = {res['RA_kN']:.2f} kN")
    print(f"RB           = {res['RB_kN']:.2f} kN")

 
    # Candidate evaluation (capacity + deflection + CO2)
   
    db = MaterialsDB("data/materials.csv")

    # Automatically scan all profiles in the CSV
    candidate_profiles = db.df["profile"].tolist()

    fy_MPa = 355.0
    gamma_M0 = 1.0
    deflection_limit_mm = (span * 1000.0) / 250.0

    print("\n=== Candidate beams ===")

    candidates = []

    for prof in candidate_profiles:
        beam = BeamSelection(profile=prof, length_m=span)
        summary = db.summary(beam)

        # Bending capacity 
        M_Rd = db.beam_M_Rd_kNm(beam, fy_MPa=fy_MPa, gamma_M0=gamma_M0)
        utilization = M_Ed / M_Rd

        # Deflection (SLS) 
        w_max_mm = max_deflection_simply_supported(
            span_m=span,
            I_cm4=summary["I_cm4"],
            q_kN_per_m=q_SLS,
            P_kN=P_SLS,
        )

        deflection_ok = w_max_mm <= deflection_limit_mm

        candidates.append(
            {
                "profile": prof,
                "M_Rd_kNm": M_Rd,
                "utilization": utilization,
                "w_max_mm": w_max_mm,
                "deflection_ok": deflection_ok,
                "mass_kg": summary["mass_kg"],
                "co2_kg": summary["co2_kg"],
            }
        )


    # Filter + optimization
    
    passing = [
        c for c in candidates
        if c["utilization"] <= 1.0 and c["deflection_ok"]
    ]

    passing_sorted = sorted(passing, key=lambda c: c["co2_kg"])

    for c in passing_sorted:
        print(
            f"{c['profile']:>7} | "
            f"u = {c['utilization']*100:5.1f}% | "
            f"w = {c['w_max_mm']:6.2f} / {deflection_limit_mm:.1f} mm | "
            f"mass = {c['mass_kg']:6.1f} kg | "
            f"CO₂ = {c['co2_kg']:7.1f} kg"
        )

    
    # Decision
    
    if not passing_sorted:
        print("\n No section satisfies bending + deflection requirements.")
    else:
        best = passing_sorted[0]
        print("\n=== Suggested low-CO₂ section (V1) ===")
        print(
            f"{best['profile']} | "
            f"utilization = {best['utilization']*100:.1f}% | "
            f"deflection = {best['w_max_mm']:.2f} mm | "
            f"CO₂ = {best['co2_kg']:.1f} kg"
        )


if __name__ == "__main__":
    main()
