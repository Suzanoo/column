import numpy as np
from utils import sum_separate, segment_area_above_line


class Column:
    def __init__(self, fc, fv, fy, Es, b, h):
        """
        b : column width in rect-section, section diameter in circular section
        h : column height in rect-section, section diameter in circular section
        """
        self.fc = fc
        self.fv = fv
        self.fy = fy
        self.Es = Es
        self.b = b
        self.h = h

    def beta_one(self):
        if self.fc <= 30:  # N/mm2(MPa)
            β1 = 0.85
        elif 30 < self.fc < 55:  # N/mm2
            β1 = 0.85 - 0.05 * (self.fc - 30) / 7
        else:
            β1 = 0.65
        self.β1 = β1

    # Effective depth
    def effective_depth(self, main_dia, traverse_dia, covering=4.5):  # cm
        self.d2 = covering + traverse_dia + main_dia / 2
        self.d = self.h - covering - traverse_dia - main_dia / 2
        print(f"d = {self.d:.2f} cm, d' = {self.d2:.2f} cm")

    # Percent Reinforcement
    def percent_reinforcment(self, Ast, Ag):
        ρg = Ast / Ag
        if 0.01 < ρg < 0.08:
            print(f"ρg = 0.01 < {ρg:.4f} < 0.08  OK ")
        else:
            print(f"ρg = {ρg:.4f} out of range [0.01, 0.08]--> Used 0.01")
            ρg = 0.01
        self.ρg = ρg

    # Safety factor, 𝜙c
    def 𝜙x(self, c, tie=True):
        """
        c : distance from top to nuetral axis
        """
        if tie == True:
            self.𝜙c = 0.65 + 0.25 * ((1 / c / self.d) - 5 / 3)  # tie
        else:
            self.𝜙c = 0.75 + 0.15 * ((1 / c / self.d) - 5 / 3)  # spiral

    # Initial column section properties
    def initialize(self, main_dia, traverse_dia, Ast, Ag):
        self.beta_one()
        self.effective_depth(main_dia, traverse_dia, covering=4.5)
        self.percent_reinforcment(Ast, Ag)

    # Calculate stress for each rebar
    def stress(self, df_rebars, c, text):
        c = c * 10  # Convert to mm
        stresses = []
        for i, row in df_rebars.iterrows():
            z = row["z"] * 10  ## Convert to mm
            if z > c:
                fs = 0.003 * (z - c) * self.Es / c
            elif z < c:
                fs = -0.003 * (c - z) * self.Es / c
            else:
                fs = 0

            # Check if absolute stress exceeds fy
            if abs(fs) > self.fy:
                fs = np.sign(fs) * self.fy  # Limit stress to fy
            stresses.append(fs)
        df_rebars[text] = stresses
        return df_rebars

    # Calculate force for each rebar
    def force(self, df_rebars, main_dia, text1, text2):
        rebar_area_mm2 = (
            np.pi * (main_dia / 2) ** 2
        )  # Cross-sectional area of rebar in mm^2
        forces = []
        for i, row in df_rebars.iterrows():
            stress = row[text1]
            if abs(stress) > self.fy:
                stress = np.sign(stress) * self.fy  # Limit stress to fy
            force = stress * rebar_area_mm2 * 1e-3  # Force in Newtons (kN)
            forces.append(force)
        df_rebars[text2] = forces
        return df_rebars

    # Calculated moment of section
    def moment(self, df_rebars, text):
        neutral_axis = (self.b / 100,)
        moment = []
        for i, row in df_rebars.iterrows():
            z = row["z"] / 100  # Convert to m
            F = row[text]

            if z < neutral_axis:
                m = -F * (neutral_axis - z)  # counter clockwise
            else:
                m = F * (z - neutral_axis)  # counter clockwise
            moment.append(m)

        return sum(moment)

    # Calculate 𝜙Pn, 𝜙Mn
    def PnMn_calculation(self, c, a, main_dia, df, text1, text2, rect=False, tie=True):
        if rect == True:
            compression_area = self.b * a * 1e2
        else:
            compression_area = segment_area_above_line(self.b, a) * 100  # mm2

        self.𝜙x(c, tie)  # set tie stirrup as defalt

        # Calculate stress of each rebars
        df = self.stress(df, c, text1)

        # Calculate force of each rebars
        df = self.force(df, main_dia, text1, text2)

        # Calculate axial force of section
        Cc = -0.85 * self.fc * compression_area * 1e-3  # kN
        Cs, Ts = sum_separate(df, text2)

        Pn = Cc + Cs + Ts
        𝜙Pn = self.𝜙c * Pn

        # print(Cc, Cs, Ts, Pn, 𝜙Pn)

        # Calculate moment
        Mc = -Cc * (self.b / 2 - a / 2) * 1e-2  # counter clockwise
        Ms = self.moment(df, text2)  # kN-m

        𝜙Mn = self.𝜙c * (Ms + Mc)

        return 𝜙Pn, 𝜙Mn[0]

    ## Pure Compression, εc = 0
    def pure_compression(self, Ast, An):
        Ast = Ast * 100  # convert to mm2
        An = An * 100  # convert to mm2

        P0 = -(0.85 * self.fc * An + self.fy * Ast) * 1e-3  # kN
        𝜙Pn = 0.65 * P0  # kN
        𝜙Pn_max = 0.85 * P0  # kN
        print(f"𝜙Pn_max = {𝜙Pn_max} kN")

        return 𝜙Pn, 𝜙Pn_max

    #  Zero Tension
    def zero_tension(self, main_dia, df, rect=False, tie=True):
        """
        εcu = 0.003
        εs = 0
        """
        c = self.d  # cm
        a = self.β1 * c  # cm
        𝜙Pn, 𝜙Mn = self.PnMn_calculation(c, a, main_dia, df, "ft0", "Ft0", rect, tie)

        return 𝜙Pn, 𝜙Mn, c

    # Balance(fs = fy)
    def balance(self, main_dia, df, rect=False, tie=True):
        """
        εcu = 0.003
        εs = εy
        """
        ey = self.fy / self.Es  # bottom rebar strain
        c = 0.003 * self.d / (0.003 + ey)
        a = self.β1 * c  # cm
        𝜙Pn, 𝜙Mn = self.PnMn_calculation(c, a, main_dia, df, "fb", "Fb", rect, tie)

        return 𝜙Pn, 𝜙Mn, c

    # Pure Bending
    def pure_bending(self, main_dia, df, rect=False, tie=True):
        """
        εcu = 0.003
        Pu = 0
        """
        # Try c
        c = self.d2  # cm

        nuetral_axis = [c]
        axial = []
        moment = []

        while True:
            a = self.β1 * c  # cm

            temp = [0]
            𝜙Pn, 𝜙Mn = self.PnMn_calculation(
                c, a, main_dia, df, "fp0", "Fp0", rect, tie
            )
            if 𝜙Pn <= 0:
                break
            elif 𝜙Pn > temp[-1]:
                c += 1  # Neutal axis < d2
            else:
                c -= 1  # Neutal axis > d2
            temp.append(𝜙Pn)

            nuetral_axis.append(c)
            axial.append(𝜙Pn)
            moment.append(𝜙Mn)

        return 𝜙Pn, 𝜙Mn, c

    ## Pure Tension
    def pure_tension(self, As):
        return -self.fy * As * 1e-3
