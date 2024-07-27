import numpy as np
import pandas as pd


from utils import *
from plot_circular import IR_diagram_plot, plot_multiple_sections, create_html
from PM import pure_compression, zero_tension, balance, pure_bending, pure_tension

import plotly.graph_objects as go


def information(dia, covering, main_dia, traverse_dia, N):
    # Calculate the inner diameter
    inner_dia = dia - 2 * covering - main_dia - traverse_dia  # for main reinforcements
    inner_dia2 = dia - 2 * covering  # for covering
    inner_dia3 = dia - 2 * covering - 2 * traverse_dia  # for traverse

    # Create the solid circle for the column section
    theta = np.linspace(0, 2 * np.pi, 100)
    x_outer = (dia / 2) * np.cos(theta)
    y_outer = (dia / 2) * np.sin(theta)

    # Create the dotted circle for the covering
    x_inner = (inner_dia2 / 2) * np.cos(theta)
    y_inner = (inner_dia2 / 2) * np.sin(theta)

    # Create the dotted circle for the traverse
    x_traverse = (inner_dia3 / 2) * np.cos(theta)
    y_traverse = (inner_dia3 / 2) * np.sin(theta)

    # Create the positions for the rebars
    theta_rebar = np.linspace(0.5 * np.pi, 2.5 * np.pi, N, endpoint=False)
    # theta_rebar = np.linspace(0, 2 * np.pi, N, endpoint=False)
    x_rebar = (inner_dia / 2) * np.cos(theta_rebar)
    y_rebar = (inner_dia / 2) * np.sin(theta_rebar)

    # Calculate distance from top of the column to each rebar
    distance_from_top = (dia / 2) - y_rebar

    # Create a DataFrame for the rebars
    rebar_data = {
        "No": list(range(1, N + 1)),
        "x": x_rebar,
        "y": y_rebar,
        "z": distance_from_top,
    }

    context = {
        "x_outer": x_outer,
        "y_outer": y_outer,
        "x_inner": x_inner,
        "y_inner": y_inner,
        "x_traverse": x_traverse,
        "y_traverse": y_traverse,
        "x_rebar": x_rebar,
        "y_rebar": y_rebar,
        "rebar_data": rebar_data,
    }

    return context


def main():
    # Input parameters
    dia = 60  # Diameter of the column in cm

    main_dia = 28  # mm
    N = 8  # Number of rebars
    traverse_dia = 12  # mm
    covering = 4.5  # Covering in cm

    fc = 24
    fy = 390  # MPa
    Es = 200000  # MPa

    Pu = 2500  # kN
    Mu = 54  # kN

    # ----------------------------------------------------------------
    beta_1 = beta_one(fc)
    Ag, Ast, An = calculate_areas(dia, main_dia / 10, N)  # cm2

    # Get the DataFrame
    data = information(dia, covering, main_dia / 10, traverse_dia / 10, N)
    df_rebars = pd.DataFrame(data["rebar_data"])
    display_table(df_rebars)

    d, d2 = effective_depth(main_dia / 10, main_dia / 10, 0, dia, covering)  # cm

    # Init
    neutral_axis = []
    x_ir = []  # 𝜙Mn
    y_ir = []  # 𝜙Pn

    ## Pure Compression
    𝜙Pn = pure_compression(fc, fy, Ast, An)
    y_ir.append(abs(𝜙Pn))
    x_ir.append(0)
    # print(f"Pure Compression : 𝜙Pn = {𝜙Pn:.2f} kN")

    ## Zero Tension
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = zero_tension(beta_1, fc, fy, Es, dia, main_dia, d, df)

    y_ir.append(abs(𝜙Pn))
    x_ir.append(𝜙Mn)
    neutral_axis.append(c)
    # display_table(df)
    print(f"Zero Tension : 𝜙Pn = {𝜙Pn:.2f} kN, 𝜙Mn = {𝜙Mn:.2f} kN-m")

    ## Balance
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = balance(beta_1, fc, fy, Es, dia, main_dia, d, df)

    y_ir.append(abs(𝜙Pn))
    x_ir.append(𝜙Mn)
    neutral_axis.append(c)
    # display_table(df)
    print(f"Balance : 𝜙Pn = {𝜙Pn:.2f} kN, 𝜙Mn = {𝜙Mn:.2f} kN-m")

    ## Pure Bending
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = pure_bending(beta_1, fc, fy, Es, dia, main_dia, d, d2, df)

    y_ir.append(0)
    x_ir.append(𝜙Mn)
    neutral_axis.append(c)
    display_table(df)
    print(f"Pure Bending : 𝜙Pn = {𝜙Pn:.2f} kN, 𝜙Mn = {𝜙Mn:.2f} kN-m")

    ## Pure Tension
    # # Area of one rebar (Ast_single)
    # radius_rebar = main_dia / 2
    # Ast_single = np.pi * (radius_rebar**2)

    # # Total area of the rebars (Ast)
    # Ast = Ast_single * N
    𝜙Pn = pure_tension(fy, Ast)
    print(f"Pure Tension : 𝜙Tn = {-𝜙Pn:.2f} kN")

    y_ir.append(𝜙Pn)
    x_ir.append(0)

    # ----------------------------------------------------------------
    # Plot section
    create_html(dia, main_dia / 10, N, data, x_ir, y_ir, Pu, Mu)

    # ----------------------------------------------------------------


# Call the main function
if __name__ == "__main__":
    print("Hello, world!")
    main()

# python app/circular.py
