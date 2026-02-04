# core/co2_calc.py
from dataclasses import dataclass
import pandas as pd
from pathlib import Path

STEEL_CO2_KG_PER_KG = 1.9  # kg CO2 per kg steel


@dataclass
class BeamSelection:
    profile: str
    length_m: float
    material: str = "steel"


class MaterialsDB:
    def __init__(self, csv_path: str | Path):
        self.csv_path = Path(csv_path)
        self.df = pd.read_csv(self.csv_path)

        required_cols = {"profile", "mass_kg_per_m"}
        missing = required_cols - set(self.df.columns)
        if missing:
            raise ValueError(
                f"Materials CSV is missing required columns: {missing}. "
                f"Found columns: {list(self.df.columns)}"
            )

    def get_section_row(self, profile: str) -> pd.Series:
        rows = self.df.loc[self.df["profile"] == profile]
        if rows.empty:
            raise KeyError(f"Profile '{profile}' not found in {self.csv_path}")
        return rows.iloc[0]

    def beam_mass_kg(self, beam: BeamSelection) -> float:
        row = self.get_section_row(beam.profile)
        mass_per_m = float(row["mass_kg_per_m"])
        return mass_per_m * beam.length_m

    def beam_co2_kg(self, beam: BeamSelection) -> float:
        mass_kg = self.beam_mass_kg(beam)
        return mass_kg * STEEL_CO2_KG_PER_KG

    def beam_M_Rd_kNm(
        self,
        beam: BeamSelection,
        fy_MPa: float = 355.0,
        gamma_M0: float = 1.0,
    ) -> float:
        """
        Bending resistance M_Rd for this beam [kNm].

        Uses:
            W_cm3 from the CSV (elastic/plastic section modulus in cm^3)
            fy_MPa as yield strength [MPa = N/mm^2]
        Formula (unit-consistent):
            M_Rd,kNm = W_cm3 * fy_MPa / (gamma_M0 * 1000)
        """
        row = self.get_section_row(beam.profile)
        W_cm3 = float(row["W_cm3"])
        M_Rd_kNm = W_cm3 * fy_MPa / (gamma_M0 * 1000.0)
        return M_Rd_kNm

    def summary(self, beam: BeamSelection) -> dict:
        row = self.get_section_row(beam.profile)
        mass_kg = self.beam_mass_kg(beam)
        co2_kg = self.beam_co2_kg(beam)

        return {
            "profile": beam.profile,
            "length_m": beam.length_m,
            "material": beam.material,
            "mass_kg_per_m": float(row["mass_kg_per_m"]),
            "mass_kg": mass_kg,
            "co2_kg": co2_kg,
            "W_cm3": float(row["W_cm3"]),
            "I_cm4": float(row["I_cm4"]),
        }
