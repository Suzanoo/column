import numpy as np
import pandas as pd

from column_gpt import StrengthCalculator, PnMnCalculator, ForceInSection

from utils import display_table


class PnMnCoordinateCalculator:
    def __init__(self, materials, geometry, reinforcement):
        self.materials = materials
        self.geometry = geometry
        self.reinforcement = reinforcement

    def pn_mn_calculator(self, df_rebars):

        # ----------------------------------------------------------------
        # Step 4: Create a Calculator object, Column object
        # ----------------------------------------------------------------
        strength_calulator = StrengthCalculator(
            self.materials, self.geometry, self.reinforcement
        )
        calculator = PnMnCalculator(
            self.materials, self.geometry, self.reinforcement, strength_calulator
        )

        force_in_section = ForceInSection(
            self.materials, self.geometry, self.reinforcement, calculator
        )

        # ----------------------------------------------------------------
        # Step 5: Perform calculations, and get IR-diagram coordinates
        # ----------------------------------------------------------------
        # initilize column properties
        force_in_section.section_properties()

        # placeholder for IR-diagram coordinates
        x_coords, y_coords = [], []

        # Calculate 𝜙Pn, 𝜙Mn as IR-diagram coordinates
        # Pure Compression
        pure_compression_results = force_in_section.compute_pure_compression()
        x_coords.append(pure_compression_results[1])  # 𝜙Mn coodinate
        y_coords.append(pure_compression_results[0])  # 𝜙Pn coodinate

        # Zero Tension (example with hypothetical arguments)
        zero_tension_results = force_in_section.compute_zero_tension(df_rebars)
        x_coords.append(zero_tension_results[1])  # 𝜙Mn coodinate
        y_coords.append(zero_tension_results[0])  # 𝜙Pn coodinate

        # Balance (example with hypothetical arguments)
        balance_results = force_in_section.compute_balance(df_rebars)
        x_coords.append(balance_results[1])  # 𝜙Mn coodinate
        y_coords.append(balance_results[0])  # 𝜙Pn coodinate

        # Pure Bending
        pure_bending_results = force_in_section.compute_pure_bending(df_rebars)
        x_coords.append(pure_bending_results[1])  # 𝜙Mn coodinate
        y_coords.append(pure_bending_results[0])  # 𝜙Pn coodinate

        # # Pure Tension
        pure_tension_results = force_in_section.compute_pure_tension()
        x_coords.append(pure_tension_results[1])  # 𝜙Mn coodinate
        y_coords.append(pure_tension_results[0])  # 𝜙Pn coodinate

        # Convert to Numpy arrays
        x_coords = np.array(x_coords)
        y_coords = np.array(y_coords)

        print("IR Coordinates : ")
        df_forces = pd.DataFrame(
            {
                "Status": [
                    "Pure Compression",
                    "Zero Tension",
                    "Balance",
                    "Pure Bending",
                    "Pure Tension",
                ],
                "𝜙Pn, kN": y_coords,
                "𝜙Mn, kN-m": x_coords,
            }
        )

        display_table(df_forces)
        return x_coords, y_coords
