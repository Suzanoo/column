import numpy as np
from tabulate import tabulate


def beta_one(fc):
    """Calculate beta1 based on concrete compressive strength."""
    if fc <= 30:  # N/mm2(MPa)
        β1 = 0.85
    elif 30 < fc < 55:  # N/mm2
        β1 = 0.85 - 0.05 * (fc - 30) / 7
    else:
        β1 = 0.65
    return β1


# Percent Reinforcement
def percent_reinforcment(Ast, Ag):
    ρg = Ast / Ag

    if 0.01 < ρg < 0.08:
        print(f"ρg = 0.01 < {ρg:.4f} < 0.08  OK ")
        return ρg
    else:
        print(f"ρg = {ρg:.4f} out of range [0.01, 0.08]--> Used 0.01")
        ρg = 0.01
        return ρg


# Effective depth
def effective_depth(𝜙1, 𝜙2, 𝜙_traverse, h, covering=4.5):  # cm
    d2 = covering + 𝜙_traverse + 𝜙2 / 2
    d = h - covering - 𝜙_traverse - 𝜙1 / 2
    print(f"d = {d:.2f} cm, d' = {d2:.2f} cm")
    return d, d2


# Display  table
def display_table(df):
    print(
        tabulate(
            df,
            headers=df.columns,
            floatfmt=".2f",
            showindex=True,
            tablefmt="psql",
        )
    )


# Sum values in a column(+ and -)
def sum_separate(df, column_name):
    # Sum of positive values in column 'F'
    positive_sum = df[df[column_name] > 0][column_name].sum()

    # Sum of negative values in column column_name
    negative_sum = df[df[column_name] < 0][column_name].sum()
    return (
        negative_sum,
        positive_sum,
    )


# Concrete and rebars area in circular section
def calculate_areas(dia, rebar_dia, N):
    # Gross section area (Ag) of the circular column
    radius = dia / 2
    Ag = np.pi * (radius**2)

    # Area of one rebar (Ast_single)
    radius_rebar = rebar_dia / 2
    Ast_single = np.pi * (radius_rebar**2)

    # Total area of the rebars (Ast)
    Ast = Ast_single * N

    # Net area of the section (Ag - Ast)
    An = Ag - Ast

    return Ag, Ast, An


def calculate_areas_in_rect(b, h, rebar_dia, N):
    # Gross section area (Ag) of the circular column
    Ag = b * h

    # Area of one rebar (Ast_single)
    radius_rebar = rebar_dia / 2
    Ast_single = np.pi * (radius_rebar**2)

    # Total area of the rebars (Ast)
    Ast = Ast_single * N

    # Net area of the section (Ag - Ast)
    An = Ag - Ast

    return Ag, Ast, An


# Segment area aboce line
def segment_area_above_line(dia, distance_from_top):
    R = dia / 2  # Radius of the column
    h = R - distance_from_top  # Distance from center of the column to the line

    if h < -R or h > R:
        # If the line is completely outside the circle, return 0 area.
        return 0 if h > R else np.pi * R**2

    # Area of the circular segment
    segment_area = R**2 * np.arccos(h / R) - h * np.sqrt(R**2 - h**2)
    return segment_area
