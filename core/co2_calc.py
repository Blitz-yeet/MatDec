# core/co2_calc.py

from __future__ import annotations

from dataclasses import dataclass
import pandas as pd
from pathlib import Path


@dataclass
class BeamSelection:
    """
    Represents a selected beam for a given span and load case.
    """
    profile: str          # e.g. "IPE 200"
    length_m: float       # beam length [m]
    material: str = "steel"  # optional tag


class MaterialsDB:
    """
    Wrapper around the materials/sections CSV generated earlier.
    """

    def __init__(self, csv_path: str | Path):
        self.csv_path = Path(csv_path)
        self.df = pd.read_csv(self.csv_path)

        required_cols = {"profile", "A_cm2", "rho_kg_per_m3", "co2_kg_per_kg"}
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
        """
        Calculate the mass of the beam in kg.
        """
        row = self.get_section_row(beam.profile)
        A_cm2 = float(row["A_cm2"])
        rho = float(row["rho_kg_per_m3"])

        # Convert area to m²: 1 cm² = 1e-4 m²
        A_m2 = A_cm2 * 1e-4

        volume_m3 = A_m2 * beam.length_m
        mass_kg = rho * volume_m3
        return mass_kg

    def beam_co2_kg(self, beam: BeamSelection) -> float:
        """
        Embodied CO₂ for the beam in kg.
        """
        row = self.get_section_row(beam.profile)
        ef = float(row["co2_kg_per_kg"])  # emission factor
        mass_kg = self.beam_mass_kg(beam)
        co2_kg = mass_kg * ef
        return co2_kg

    def summary(self, beam: BeamSelection) -> dict:
        """
        Small helper to return a dict with all key numbers.
        """
        row = self.get_section_row(beam.profile)
        mass_kg = self.beam_mass_kg(beam)
        co2_kg = self.beam_co2_kg(beam)

        return {
            "profile": beam.profile,
            "length_m": beam.length_m,
            "material": beam.material,
            "A_cm2": float(row["A_cm2"]),
            "rho_kg_per_m3": float(row["rho_kg_per_m3"]),
            "co2_kg_per_kg": float(row["co2_kg_per_kg"]),
            "mass_kg": mass_kg,
            "co2_kg": co2_kg,
        }
