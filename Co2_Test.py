from core.co2_calc import MaterialsDB, BeamSelection

db = MaterialsDB("data/materials.csv")

beam = BeamSelection(profile="IPE 200", length_m=6.0)
summary = db.summary(beam)
M_Rd = db.beam_M_Rd_kNm(beam, fy_MPa=355.0, gamma_M0=1.0)

print(summary)
print(f"M_Rd = {M_Rd:.2f} kNm")
