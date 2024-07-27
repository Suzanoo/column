import numpy as np
from utils import sum_separate, segment_area_above_line


# Safety factor, 𝜙c
def 𝜙x(c, d):
    # 𝜙x = 0.65 + 0.25 * ((1 / c / d) - 5 / 3)  # tie
    𝜙x = 0.75 + 0.15 * ((1 / c / d) - 5 / 3)  # spiral
    return 𝜙x


def stress(df_rebars, c, fy, Es, text):
    # Calculate stress for each rebar
    c = c * 10  # Convert to mm
    stresses = []
    for i, row in df_rebars.iterrows():
        z = row["z"] * 10  ## Convert to mm
        if z > c:
            fs = 0.003 * (z - c) * Es / c
        elif z < c:
            fs = -0.003 * (c - z) * Es / c
        else:
            fs = 0

        # Check if absolute stress exceeds fy
        if abs(fs) > fy:
            fs = np.sign(fs) * fy  # Limit stress to fy
        stresses.append(fs)
    df_rebars[text] = stresses
    return df_rebars


def force(df_rebars, main_dia, fy, text1, text2):
    # Calculate force for each rebar
    rebar_area_mm2 = (
        np.pi * (main_dia / 2) ** 2
    )  # Cross-sectional area of rebar in mm^2
    forces = []
    for i, row in df_rebars.iterrows():
        stress = row[text1]
        if abs(stress) > fy:
            stress = np.sign(stress) * fy  # Limit stress to fy
        force = stress * rebar_area_mm2 * 1e-3  # Force in Newtons (kN)
        forces.append(force)
    df_rebars[text2] = forces
    return df_rebars


def moment(df_rebars, neutral_axis, text):
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


# P-M Calculation
def pm_calculation(
    fc, fy, Es, c, a, dia, main_dia, d, df, text1, text2, b=0, rect=False
):
    if rect == True:
        compression_area = b * a * 1e2
    else:
        compression_area = segment_area_above_line(dia, a) * 100  # mm2

    𝜙 = 𝜙x(c, d)

    # Calculate stress of each rebars
    df = stress(df, c, fy, Es, text1)

    # Calculate force of each rebars
    df = force(df, main_dia, fy, text1, text2)

    # Calculate axial force of section
    Cc = -0.85 * fc * compression_area * 1e-3  # kN
    Cs, Ts = sum_separate(df, text2)

    Pn = Cc + Cs + Ts
    𝜙Pn = 𝜙 * Pn

    # print(Cc, Cs, Ts, Pn, 𝜙Pn)

    # Calculate moment
    Mc = -Cc * (dia / 2 - a / 2) * 1e-2  # counter clockwise
    Ms = moment(df, dia / 100, text2)  # kN-m

    𝜙Mn = 𝜙 * (Ms + Mc)

    return 𝜙Pn, 𝜙Mn


## Pure Compression
def pure_compression(fc, fy, Ast, An):
    Ast = Ast * 100  # convert to mm2
    An = An * 100  # convert to mm2
    # Nominal axial compressive strength at zero eccentricity
    P0 = -(0.85 * fc * An + fy * Ast) * 1e-3  # kN, ACI 318-14 (22.4.2.2)

    # Factored axial compressive strength at zero eccentricity
    𝜙Pn = 0.65 * P0  # ACI 318-14 (Table 21.2.2)
    𝜙Pn_max = 0.8 * P0

    return 𝜙Pn


#  Bar Stress Near Tension Face of Member Equal to Zero, ( εs = fs = 0 )
def zero_tension(beta_1, fc, fy, Es, dia, main_dia, d, df, b=0, rect=False):
    c = d  # Distance of the neutral axis from the top of the column in cm
    a = beta_1 * c  # cm
    𝜙Pn, 𝜙Mn = pm_calculation(
        fc, fy, Es, c, a, dia, main_dia, d, df, "ft0", "Ft0", b, rect
    )

    return 𝜙Pn, 𝜙Mn, c


#  Bar Stress Near Tension Face of Member Equal to fy, ( fs = - fy )
def balance(beta_1, fc, fy, Es, dia, main_dia, d, df, b=0, rect=False):
    ey = fy / Es  # bottom rebar strain
    c = 0.003 * d / (0.003 + ey)
    a = beta_1 * c  # cm
    𝜙Pn, 𝜙Mn = pm_calculation(
        fc, fy, Es, c, a, dia, main_dia, d, df, "fb", "Fb", b, rect
    )

    return 𝜙Pn, 𝜙Mn, c


def pure_bending(beta_1, fc, fy, Es, dia, main_dia, d, d2, df, b=0, rect=False):
    # Try c
    c = d2  # cm
    while True:
        a = beta_1 * c  # cm

        temp = [0]
        𝜙Pn, 𝜙Mn = pm_calculation(
            fc, fy, Es, c, a, dia, main_dia, d, df, "fp0", "Fp0", b, rect
        )
        if 𝜙Pn <= 0:
            break
        elif 𝜙Pn > temp[-1]:
            c += 1  # Neutal axis < d2
        else:
            c -= 1  # Neutal axis > d2
        temp.append(𝜙Pn)

    return 𝜙Pn, 𝜙Mn, c


## Pure Tension
def pure_tension(fy, As):
    return -fy * As * 1e-3
