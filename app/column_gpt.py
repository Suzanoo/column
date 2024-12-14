import numpy as np

from utils import display_table, sum_separate


class MaterialProperties:
    def __init__(self, fc, fv, fy, Es):
        self.fc = fc  # Concrete compressive strength (MPa)
        self.fv = fv  # Steel yield strength (MPa) of round bar
        self.fy = fy  # Steel yield strength (MPa) of deform bar
        self.Es = Es  # Steel elastic modulus (MPa)

    def εy(self):
        return self.fy / self.Es  # Yield strain

    def beta_one(self):
        """
        Calculate the β1 factor based on fc.
        """
        if self.fc <= 30:  # N/mm2(MPa)
            return 0.85
        elif 30 < self.fc < 55:  # N/mm2
            return 0.85 - 0.05 * (self.fc - 30) / 7
        else:
            return 0.65


class SectionGeometry:
    def __init__(self, b, h):
        self.b = b  # Column width (cm)
        self.h = h  # Column height (cm)


class Reinforcement:
    def __init__(self, main_dia, traverse_dia, N):
        self.main_dia = main_dia  # main reinforcement (mm)
        self.traverse_dia = traverse_dia  # traverse reinforcement (mm)
        self.N = N  # number 0f main reinforcement


class SectionProperties:
    def __init__(self, geometry, reinforcement):
        self.geometry = geometry
        self.reinforcement = reinforcement

    def effective_depth(self, covering=4.5):
        """
        Calculate effective depth (d) and effective cover (d_prime).
        covering: float, optional
            Concrete cover in cm (default: 4.5 cm).
        Returns:
            tuple: (d, d_prime) in cm.
        """
        d_prime = (
            covering
            + self.reinforcement.traverse_dia / 10
            + self.reinforcement.main_dia / 20  # Divide by 20 for radius
        )
        d = (
            self.geometry.h
            - covering
            - self.reinforcement.traverse_dia / 10
            - self.reinforcement.main_dia / 20
        )
        print(f"d = {d:.2f} cm, d' = {d_prime:.2f} cm")
        return d, d_prime

    def section_area(self):
        """
        Calculate gross section area (Ag), net area (An), and reinforcement area (Ast).
        Returns:
            tuple: (Ag, Ast, An) in cm^2.
        """
        Ag = self.geometry.b * self.geometry.h  # Gross section area, cm^2
        Ast = (
            self.reinforcement.N * np.pi * ((self.reinforcement.main_dia / 10) ** 2) / 4
        )  # Reinforcement area, cm^2
        An = Ag - Ast  # Net area, cm^2
        return Ag, Ast, An

    def validate_reinforcement_ratio(self):
        """
        Validate if the reinforcement ratio is within acceptable limits (0.01 <= rho_g <= 0.08).
        Returns:
            float: Validated reinforcement ratio.
        Raises:
            ValueError: If the reinforcement ratio is out of range.
        """
        Ag, Ast, _ = self.section_area()
        rho_g = Ast / Ag
        if 0.01 <= rho_g <= 0.08:
            return rho_g
        raise ValueError(
            f"Reinforcement ratio {rho_g:.4f} is out of range. Valid range is 0.01 to 0.08."
        )


class StrengthCalculator:
    def __init__(self, materials, geometry, reinforcement):
        self.materials = materials
        self.geometry = geometry
        self.reinforcement = reinforcement

    def calculate_phi_factor(self, c):
        """
        Calculate the strength reduction factor (φ) based on c and d.
        c = nuetral axis from top edge of section
        """
        if c == 0:
            return 0.65
        else:
            d_ratio = c / self.geometry.h
            return 0.65 + 0.25 * (1 - 5 / (3 * d_ratio))

    # Calculate stress for each rebar
    def calculate_stress(self, df_rebars, c):
        """
        Calculate the stress in each rebar.
        """
        stresses = []
        for _, row in df_rebars.iterrows():
            z = row["z"] * 10  # Convert cm to mm
            strain = 0.003 * abs(z - c) / c if z != c else 0
            fs = min(
                strain * self.materials.Es, self.materials.fy
            )  # Limit stress to fy
            stresses.append(fs)
        df_rebars["stress"] = stresses  # MPa
        return df_rebars

    def calculate_force(self, df_rebars):
        """
        Calculate the force in each rebar.
        """
        rebar_area = np.pi * (self.reinforcement.main_dia / 2) ** 2  # mm2
        df_rebars["force"] = df_rebars["stress"] * rebar_area * 1e-3  # kN
        return df_rebars

    def calculate_moment(self, df_rebars, c):
        """
        Calculate the moment contribution from each rebar.
        """
        moments = [
            row["force"] * (row["z"] - c) * 1e-2 for _, row in df_rebars.iterrows()
        ]
        return sum(moments)

    def calculate_pn_mn(self, c, a, df_rebars):
        """
        Calculate axial load (Pn) and moment (Mn) for a given neutral axis depth.
        """
        comp_area = self.geometry.b * a * 1e2  # cm2 to mm2
        Cc = -0.85 * self.materials.fc * comp_area * 1e-3  # Compression in concrete, kN
        df_rebars = self.calculate_stress(df_rebars, c)
        df_rebars = self.calculate_force(df_rebars)
        Cs, Ts = sum_separate(df_rebars, "force")
        Pn = Cc + Cs + Ts
        Mc = Cc * (c - a / 2) * 1e-2
        Ms = self.calculate_moment(df_rebars, c)
        Mn = Mc + Ms
        return self.calculate_phi_factor(c) * Pn, self.calculate_phi_factor(c) * Mn


class PnMnCalculator:
    def __init__(self, materials, geometry, reinforcement, strength_calculator):
        self.materials = materials
        self.geometry = geometry
        self.reinforcement = reinforcement
        self.calculator = strength_calculator

        self.β1 = materials.beta_one()
        self.εy = materials.εy()

    def pure_compression(self, An, Ast):
        P0 = (
            -(0.85 * self.materials.fc * An * 1e2 + self.materials.fy * Ast * 1e2)
            * 1e-3
        )  # kN
        𝜙Pn = 0.65 * P0
        𝜙Pn_max = 0.85 * P0
        print(f"Pure Compression : 𝜙Pn = {𝜙Pn:.2f} kN")
        return 𝜙Pn, 0  # kN, kN-m

    def pure_tension(self, Ast):
        𝜙Pn = -self.materials.fy * Ast * 1e-3
        print(f"Pure Tension : 𝜙Pn = {𝜙Pn:.2f} kN")
        return 𝜙Pn, 0  # kN, kN-m

    def zero_tension(self, df):
        c = self.geometry.h
        a = self.β1 * c
        # Placeholder for PnMn_calculation
        𝜙Pn, 𝜙Mn = self.calculator.calculate_pn_mn(c, a, df)
        print(f"Zero Tension : 𝜙Pn, 𝜙Mn = {𝜙Pn:.2f} kN, {𝜙Mn:.2f} kN-m")
        display_table(df)
        return 𝜙Pn, 𝜙Mn

    def balance(self, df):
        c = 0.003 * self.geometry.h / (0.003 + self.εy)
        a = self.β1 * c
        # Placeholder for PnMn_calculation
        𝜙Pn, 𝜙Mn = self.calculator.calculate_pn_mn(c, a, df)
        print(f"Balance : 𝜙Pn, 𝜙Mn = {𝜙Pn:.2f} kN, {𝜙Mn:.2f} kN-m")
        display_table(df)
        return 𝜙Pn, 𝜙Mn

    def pure_bending(self, df):
        """
        Calculate pure bending condition (εcu = 0.003, Pu = 0).

        Parameters:
            main_dia (float): Diameter of main reinforcement bars (cm)
            df (DataFrame): Rebar data

        Returns:
            tuple: 𝜙Pn (axial strength), 𝜙Mn (moment strength), c (neutral axis depth)
        """
        c = self.geometry.h  # cm (initial assumption for neutral axis depth)
        neutral_axis, axial, moment = [c], [], []

        while True:
            a = self.β1 * c  # cm
            𝜙Pn, 𝜙Mn = self.calculator.calculate_pn_mn(c, a, df)
            if 𝜙Pn <= 0:
                break
            elif len(axial) > 0 and 𝜙Pn < axial[-1]:
                c -= 1  # Adjust for neutral axis > depth
            else:
                c += 1  # Adjust for neutral axis < depth

            neutral_axis.append(c)
            axial.append(𝜙Pn)
            moment.append(𝜙Mn)

        print(f"Pure Bending : 𝜙Pn, 𝜙Mn = {𝜙Pn:.2f} kN, {𝜙Mn:.2f} kN-m")
        display_table(df)
        return 𝜙Pn, 𝜙Mn


class ForceInSection:
    def __init__(self, materials, geometry, reinforcement, force):
        self.materials = materials
        self.geometry = geometry
        self.reinforcement = reinforcement
        self.force = force

    def section_properties(self):
        prop = SectionProperties(self.geometry, self.reinforcement)
        d, d_prime = prop.effective_depth()
        self.Ag, self.Ast, self.An = prop.section_area()
        rho_g = prop.validate_reinforcement_ratio()

    def compute_pure_compression(self):
        return self.force.pure_compression(self.An, self.Ast)

    def compute_pure_tension(self):
        return self.force.pure_tension(self.Ast)

    def compute_zero_tension(self, df):
        return self.force.zero_tension(df)

    def compute_balance(self, df):
        return self.force.balance(df)

    def compute_pure_bending(self, df):
        return self.force.pure_bending(df)
