import csv
from pathlib import Path

# This part defines the path to the materials CSV file
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MATERIALS_CSV = PROJECT_ROOT / "data" / "materials.csv"

# Density of steel in kg/m3
STEEL_DENSITY = 7850.0 

# This function loads the sections from the CSV file
def load_sections():
    sections = {}

    with open(MATERIALS_CSV, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:

            # Name of the profile
            name = row["profile"]  

            # Mass per meter (kg/m)
            mass_per_m = float(row["mass_kg_per_m"])

            # Convert I and W from cm^4 / cm^3 to m^4 / m^3
            I_m4 = float(row["I_cm4"]) * 1e-8
            W_m3 = float(row["W_cm3"]) * 1e-6

            # Compute cross-section area A [m2] from mass_per_m and density
            A_m2 = mass_per_m / STEEL_DENSITY

            # Store everything in SI units
            sections[name] = {
                "A": A_m2,               # m2
                "I": I_m4,               # m4
                "W": W_m3,               # m3
                "mass_per_m": mass_per_m # kg/m
            }

    return sections

# This function retrieves a specific section by name
def get_section(name: str) -> dict:
    sections = load_sections()

    if name not in sections:
        raise ValueError(f"Section '{name}' not found in materials.csv")

    return sections[name]


if __name__ == "__main__":
    secs = load_sections()
    print(f"Loaded {len(secs)} sections")
    example_name = next(iter(secs.keys()))
    print(example_name, "→", secs[example_name])
