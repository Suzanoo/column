import numpy as np
import pandas as pd

from absl import app, flags, logging
from absl.flags import FLAGS


from utils import get_valid_integer, calculate_areas, display_table
from plot_circular import create_plot, create_html
from column import Column


flags.DEFINE_float("fc", 24, "240ksc, MPa")
flags.DEFINE_integer("fy", 395, "SD40 main bar, MPa")
flags.DEFINE_integer("fv", 235, "SR24 traverse, MPa")
flags.DEFINE_integer("Es", 200000, "Young's modulus ,MPa")
flags.DEFINE_float("c", 4, "concrete covering, cm")

flags.DEFINE_float("Pu", 0, "Axial force, kN")
flags.DEFINE_float("Mux", 0, "Mux, kN-m")
flags.DEFINE_float("Muy", 0, "Mux, kN-m")


def information(section_dia, covering, main_dia, traverse_dia, N):
    # Calculate the inner diameter
    inner_dia = (
        section_dia - 2 * covering - main_dia - traverse_dia
    )  # for main reinforcements
    inner_dia2 = section_dia - 2 * covering  # for covering
    inner_dia3 = section_dia - 2 * covering - 2 * traverse_dia  # for traverse

    # Create the solid circle for the column section
    theta = np.linspace(0, 2 * np.pi, 100)
    x_outer = (section_dia / 2) * np.cos(theta)
    y_outer = (section_dia / 2) * np.sin(theta)

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
    distance_from_top = (section_dia / 2) - y_rebar

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


def create_ir_diagram(section_dia, main_dia, N, traverse_dia, stirrup_type):

    covering = FLAGS.c  # Covering in cm

    # Load
    Pu = FLAGS.Pu  # kN
    Mux = FLAGS.Mux  # kN
    Muy = FLAGS.Muy  # kN
    Mu = np.sqrt(Mux * Mux + Muy * Muy)

    # ----------------------------------------------------------------
    # Calculalte concrete and rebars area
    Ag, Ast, An = calculate_areas(section_dia, main_dia / 10, N)  # cm2

    # Instanciated
    column = Column(
        fc=FLAGS.fc,
        fv=FLAGS.fv,
        fy=FLAGS.fy,
        Es=FLAGS.Es,
        b=section_dia,
        h=section_dia,
        section="circle",
        stirrup=stirrup_type,
    )
    column.initialize(main_dia / 10, traverse_dia / 10, Ast, An, Ag)
    column.traverse(An, Ag, main_dia / 10, traverse_dia / 10)

    # Get rebars coordinates
    data = information(section_dia, covering, main_dia / 10, traverse_dia / 10, N)
    df_rebars = pd.DataFrame(data["rebar_data"])

    print(f"\n[INFO] Rebars coodinates(x, y) and distance from top edge(z), cm ")
    # display_table(df_rebars)

    # Initialized
    neutral_axis = []
    x_ir = []  # 𝜙Mn
    y_ir = []  # 𝜙Pn

    ## 1-Pure Compression
    𝜙Pn, 𝜙Pn_max = column.pure_compression(Ast, An)
    y_ir.append(abs(𝜙Pn))
    x_ir.append(0)

    ## 2-Zero Tension
    𝜙Pn, 𝜙Mn, c = column.zero_tension(main_dia, df_rebars)

    y_ir.append(abs(𝜙Pn))
    x_ir.append(𝜙Mn)
    neutral_axis.append(c)

    ## 3-Balance
    𝜙Pn, 𝜙Mn, c = column.balance(main_dia, df_rebars)

    y_ir.append(abs(𝜙Pn))
    x_ir.append(𝜙Mn)
    neutral_axis.append(c)

    ## 4-Pure Bending
    𝜙Pn, 𝜙Mn, c = column.pure_bending(main_dia, df_rebars)

    y_ir.append(0)
    x_ir.append(𝜙Mn)
    neutral_axis.append(c)

    ## 5-Pure Tension
    # # Area of one rebar (Ast_single)
    # radius_rebar = main_dia / 2
    # Ast_single = np.pi * (radius_rebar**2)

    # # Total area of the rebars (Ast)
    # Ast = Ast_single * N
    𝜙Pn = column.pure_tension(Ast)

    y_ir.append(𝜙Pn)
    x_ir.append(0)

    df = pd.DataFrame(
        {
            "Status": [
                "Pure Compression",
                "Zero Tension",
                "Balance",
                "Pure Bending",
                "Pure Tension",
            ],
            "𝜙Pn, kN": y_ir,
            "𝜙Mn, kN-m": x_ir,
        }
    )

    print(f"\n[INFO] IR-Diagram coordinates : ")
    print(f"𝜙Pn_max = {abs(𝜙Pn_max):.2f} kN")
    display_table(df)

    section_fig, ir_fig = create_plot(
        section_dia / 2, section_dia, main_dia / 10, N, data, x_ir, y_ir, Pu, Mu
    )

    return section_fig, ir_fig


def main(argv):
    print("====================== Circular Column Design ======================")
    print("[INFO] Section properties : ")
    print(
        f"fc: {FLAGS.fc} MPa, fv: {FLAGS.fv} MPa, fy: {FLAGS.fy} MPa, Es: {FLAGS.Es} MP"
    )
    print(f"Pu: {FLAGS.Pu} kN, Mux: {FLAGS.Mux} kN-m, Muy: {FLAGS.Muy} kN-m")

    n = 1
    section_fig = []
    ir_fig = []

    while True:
        print(f"\n============== Section {n} ==============")

        # Input parameters
        while True:
            section_dia = get_valid_integer("Define section diameter in cm : ")
            main_dia = get_valid_integer("Main reinforcement diameter in mm : ")
            N = get_valid_integer("Numbers of Main reinforcement : ")
            traverse_dia = get_valid_integer("Traverse reinforcement in mm : ")

            stirrup = input("Stirrup is 'tie' or 'spiral' select  T|S : ").upper()
            if stirrup in ["T", "t"]:
                stirrup_type = "tie"
            else:
                stirrup_type = "spiral"

            ask = input("Confirm! Y|N :").upper()
            if ask == "Y":
                break
            else:
                pass

        section, ir = create_ir_diagram(
            section_dia, main_dia, N, traverse_dia, stirrup_type
        )

        section_fig.append(section)
        ir_fig.append(ir)

        ask = input("Any section? , Y|N : ").upper()
        if ask == "N":
            break
        else:
            n += 1

    create_html(section_fig, ir_fig)

    # ----------------------------------------------------------------


# Call the main function
if __name__ == "__main__":
    print("Hello, world!")
    app.run(main)

# python app/circular.py  --Pu=2500 --Mux=125 --Muy=45
