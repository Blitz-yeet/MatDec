# main_beam_demo.py
from core.loads import LoadCase, UDL, PointLoad, analyze_simply_supported
from core.co2_calc import MaterialsDB, BeamSelection


def main():
    # 1) Geometry and loads
    span = 6.0  # m

    # Example ULS load case (already factored for demo):
    #   - 15 kN/m UDL along entire span
    #   - 30 kN point load in midspan
    lc = LoadCase(
        name="ULS",
        span_m=span,
        udls=[UDL(intensity_kN_per_m=-15.0, start_m=0.0, end_m=span)],
        point_loads=[PointLoad(value_kN=-30.0, position_m=span / 2)],
        gamma=1.0,  # factors already included above
    )

    # 2) Structural analysis: get design bending moment M_Ed
    res = analyze_simply_supported(lc)
    M_Ed = res["M_max_kNm"]

    print("=== Structural analysis ===")
    print(f"Span L       = {span:.2f} m")
    print(f"M_Ed,max     = {M_Ed:.2f} kNm")
    print(f"RA           = {res['RA_kN']:.2f} kN")
    print(f"RB           = {res['RB_kN']:.2f} kN")

    # 3) CO₂ + capacity check for a set of candidate profiles
    db = MaterialsDB("data/materials.csv")

    candidate_profiles = [
        "IPE 160",
        "IPE 180",
        "IPE 200",
        "IPE 220",
        "IPE 240",
    ]  # make sure these exist in your CSV

    print("\n=== Candidates (capacity + CO₂) ===")
    candidates = []

    for prof in candidate_profiles:
        beam = BeamSelection(profile=prof, length_m=span)
        summary = db.summary(beam)
        M_Rd = db.beam_M_Rd_kNm(beam, fy_MPa=355.0, gamma_M0=1.0)
        utilization = M_Ed / M_Rd

        candidates.append(
            {
                "profile": prof,
                "M_Rd_kNm": M_Rd,
                "utilization": utilization,
                "mass_kg": summary["mass_kg"],
                "co2_kg": summary["co2_kg"],
            }
        )

    # keep only sections that satisfy bending (u <= 1.0) and sort by CO₂
    passing = [c for c in candidates if c["utilization"] <= 1.0]
    passing_sorted = sorted(passing, key=lambda c: c["co2_kg"])

    for c in passing_sorted:
        print(
            f"{c['profile']:>7} | "
            f"M_Rd = {c['M_Rd_kNm']:8.1f} kNm | "
            f"u = {c['utilization']*100:5.1f} % | "
            f"mass = {c['mass_kg']:6.1f} kg | "
            f"CO₂ = {c['co2_kg']:7.1f} kg"
        )

    if not passing_sorted:
        print("\nNo candidate meets the bending requirement.")
    else:
        best = passing_sorted[0]
        print("\n=== Suggested low-CO₂ choice ===")
        print(
            f"{best['profile']} with utilization {best['utilization']*100:.1f} % "
            f"and CO₂ {best['co2_kg']:.1f} kg"
        )


if __name__ == "__main__":
    main()
