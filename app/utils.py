import numpy as np
from tabulate import tabulate


def get_valid_integer(prompt):
    while True:
        user_input = input(prompt)
        if user_input.isdigit():
            return int(user_input)
        else:
            print("Invalid input. Please enter a valid number.")


def convert_input_to_list(input_string):
    return list(map(int, input_string.split()))


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


# Sum values in a df column(+ and -)
def sum_separate(df, column_name):
    # Sum of positive values in column 'F'
    positive_sum = df[df[column_name] > 0][column_name].sum()

    # Sum of negative values in column column_name
    negative_sum = df[df[column_name] < 0][column_name].sum()
    return (
        negative_sum,
        positive_sum,
    )


# Compute concrete and rebars area in circular section
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


# Compute concrete and rebars area in rectangle section
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


# Segment area above line
def segment_area_above_line(dia, distance_from_top):
    R = dia / 2  # Radius of the column
    h = R - distance_from_top  # Distance from center of the column to the line

    if h < -R or h > R:
        # If the line is completely outside the circle, return 0 area.
        return 0 if h > R else np.pi * R**2

    # Area of the circular segment
    segment_area = R**2 * np.arccos(h / R) - h * np.sqrt(R**2 - h**2)
    return segment_area
