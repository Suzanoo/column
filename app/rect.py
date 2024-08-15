import pandas as pd

from absl import app, flags
from absl.flags import FLAGS

from plot_rect import (
    get_rebar_coordinates,
    create_plot,
    create_html,
)
from utils import (
    get_valid_integer,
    convert_input_to_list,
    display_table,
    calculate_areas_in_rect,
)
from column import Column

## FLAGS definition
# https://stackoverflow.com/questions/69471891/clarification-regarding-abseil-library-flags

flags.DEFINE_float("fc", 23.5, "240ksc, MPa")
flags.DEFINE_integer("fy", 395, "SD40 main bar, MPa")
flags.DEFINE_integer("fv", 235, "SR24 traverse, MPa")
flags.DEFINE_integer("Es", 200000, "Young's modulus ,MPa")
flags.DEFINE_float("c", 4, "concrete covering, cm")

# flags.DEFINE_integer("main", 12, "main reinforcement, mm")
# flags.DEFINE_integer("trav", 6, "traverse reinforcement, mm")
flags.DEFINE_float("b", 0, "width, cm")
flags.DEFINE_float("h", 0, "depth, cm")
flags.DEFINE_float("Pu", 0, "Axial force, kN")
flags.DEFINE_float("Mux", 0, "Mux, kN-m")
flags.DEFINE_float("Muy", 0, "Mux, kN-m")


# ----------------------------------------------------------------
## X-X Axis
# ----------------------------------------------------------------
def x_axis(main_dia, N, df_rebars, column):
    nuetral_axis = []
    x_ir_mux = []  # 𝜙Mn
    y_ir_mux = []  # 𝜙Pn

    Ag, Ast, An = calculate_areas_in_rect(FLAGS.b, FLAGS.h, main_dia / 10, N)  # cm2

    print(f"\n[INFO] Rebars coodinates(x, y) and distance from top edge(z), cm ")
    display_table(df_rebars)

    ## 1-Pure Compression
    𝜙Pn, 𝜙Pn_max = column.pure_compression(Ast, An)
    y_ir_mux.append(abs(𝜙Pn))
    x_ir_mux.append(0)

    ## 2-Zero Tension
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = column.zero_tension(main_dia, df, rect=True)

    y_ir_mux.append(abs(𝜙Pn))
    x_ir_mux.append(𝜙Mn)
    nuetral_axis.append(c)

    ## 3-Balance
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = column.balance(main_dia, df, rect=True)

    y_ir_mux.append(abs(𝜙Pn))
    x_ir_mux.append(𝜙Mn)
    nuetral_axis.append(c)

    ## 4-Pure Bending
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = column.pure_bending(main_dia, df, rect=True)

    y_ir_mux.append(0)
    x_ir_mux.append(𝜙Mn)
    nuetral_axis.append(c)

    ## 5-Pure Tension
    𝜙Pn = column.pure_tension(Ast * 1e2)

    y_ir_mux.append(𝜙Pn)
    x_ir_mux.append(0)

    df = pd.DataFrame(
        {
            "Status": [
                "Pure Compression",
                "Zero Tension",
                "Balance",
                "Pure Bending",
                "Pure Tension",
            ],
            "𝜙Pn, kN": y_ir_mux,
            "𝜙Mn, kN-m": x_ir_mux,
        }
    )
    print(f"\n[INFO] IR-Diagram coordinates : ")
    print(f"𝜙Pn_max = {abs(𝜙Pn_max):.2f} kN")
    display_table(df)

    return x_ir_mux, y_ir_mux


# ----------------------------------------------------------------
## Y-Y Axis
# ----------------------------------------------------------------
def y_axis(main_dia, N, df_rebars, column):
    """
    With Y-Y axis
    we swapp b, h and calculate distance from top of rebar (z)
    """
    nuetral_axis = []
    x_ir_muy = []  # 𝜙Mn
    y_ir_muy = []  # 𝜙Pn

    Ag, Ast, An = calculate_areas_in_rect(FLAGS.b, FLAGS.h, main_dia / 10, N)  # cm2

    # Get the rebar coordinates
    # Create a new DataFrame with swapped 'x' and 'y' columns
    df_swapped = df_rebars.copy()[["x", "y"]].rename(columns={"x": "y", "y": "x"})

    # Rearrange the columns to [x, y]
    df_swapped = df_swapped[["x", "y"]]

    # Calculate distance from top
    df_swapped["z"] = FLAGS.h - df_swapped["y"]

    print(f"\n[INFO] Rebars coodinates(x, y) and distance from top edge(z), cm ")
    display_table(df_swapped)

    ## 1-Pure Compression
    𝜙Pn, 𝜙Pn_max = column.pure_compression(Ast, An)
    y_ir_muy.append(abs(𝜙Pn))
    x_ir_muy.append(0)

    ## 2-Zero Tension
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = column.zero_tension(main_dia, df_swapped, rect=True)

    y_ir_muy.append(abs(𝜙Pn))
    x_ir_muy.append(𝜙Mn)
    nuetral_axis.append(c)

    ## 3-Balance
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = column.balance(main_dia, df_swapped, rect=True)

    y_ir_muy.append(abs(𝜙Pn))
    x_ir_muy.append(𝜙Mn)
    nuetral_axis.append(c)

    ## 4-Pure Bending
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = column.pure_bending(main_dia, df_swapped, rect=True)

    y_ir_muy.append(0)
    x_ir_muy.append(𝜙Mn)
    nuetral_axis.append(c)

    ## 5-Pure Tension
    𝜙Pn = column.pure_tension(Ast * 1e2)

    y_ir_muy.append(𝜙Pn)
    x_ir_muy.append(0)

    df = pd.DataFrame(
        {
            "Status": [
                "Pure Compression",
                "Zero Tension",
                "Balance",
                "Pure Bending",
                "Pure Tension",
            ],
            "𝜙Pn, kN": y_ir_muy,
            "𝜙Mn, kN-m": x_ir_muy,
        }
    )
    print(f"\n[INFO] IR-Diagram coordinates : ")
    print(f"𝜙Pn_max = {abs(𝜙Pn_max):.2f} kN")
    display_table(df)

    return x_ir_muy, y_ir_muy


# ----------------------------------------------------------------
## Main function
# ----------------------------------------------------------------
def create_ir_diagram(main_dia, traverse_dia):
    # Lay rebars
    while True:

        bottom_layers = convert_input_to_list(
            input("Define list of bottom reinforcement for each layer, ex. 3 2 2 : ")
        )
        top_layers = convert_input_to_list(
            input("Define list of top reinforcement for each layer, ex. 3 2 : ")
        )
        middle_rebars = get_valid_integer("Define middle rebars ex.4 : ")

        ask = input("Confirm! Y|N :").upper()
        if ask == "Y":
            print("Goodbye!")
            break
        else:
            pass

    # Total rebars
    N = sum(bottom_layers + top_layers)

    # Get the rebar coordinates
    df_rebars = get_rebar_coordinates(
        FLAGS.b,
        FLAGS.h,
        FLAGS.c,
        main_dia / 10,
        traverse_dia / 10,
        bottom_layers,
        top_layers,
        middle_rebars,
    )

    # Calculalte concrete and rebars area
    Ag, Ast, An = calculate_areas_in_rect(FLAGS.b, FLAGS.h, main_dia / 10, N)  # cm2

    print(f"\nX-X Axis")
    # Instanciated
    column = Column(
        FLAGS.fc, FLAGS.fv, FLAGS.fy, FLAGS.Es, FLAGS.b, FLAGS.h, stirrup="tie"
    )
    column.initialize(main_dia / 10, traverse_dia / 10, Ast, Ag)

    # Coordinate for IR-diagrams for Mux
    x_ir_mux, y_ir_mux = x_axis(main_dia, N, df_rebars, column)

    print(f"\nY-Y Axis")
    # Instanciated
    column = Column(
        FLAGS.fc, FLAGS.fv, FLAGS.fy, FLAGS.Es, FLAGS.h, FLAGS.b, stirrup="tie"
    )  # Swapp b, h
    column.initialize(main_dia / 10, traverse_dia / 10, Ast, Ag)

    # Coordinate for IR-diagrams for Muy
    x_ir_muy, y_ir_muy = y_axis(main_dia, N, df_rebars, column)

    section_fig, ir_fig = create_plot(
        FLAGS.b,
        FLAGS.h,
        FLAGS.c,
        traverse_dia,
        main_dia,
        bottom_layers,
        top_layers,
        middle_rebars,
        x_ir_mux,
        y_ir_mux,
        x_ir_muy,
        y_ir_muy,
        FLAGS.Pu,
        FLAGS.Mux,
        FLAGS.Muy,
    )

    return section_fig, ir_fig


def main(argv):
    print("====================== Rectangular Column Design ======================")
    print("[INFO] Section properties : ")
    print(
        f"fc: {FLAGS.fc} MPa, fv: {FLAGS.fv} MPa, fy: {FLAGS.fy} MPa, Es: {FLAGS.Es} MP"
    )
    print(f"width: {FLAGS.b} cm, depth: {FLAGS.h} cm")
    print(f"Pu: {FLAGS.Pu} kN, Mux: {FLAGS.Mux} kN-m, Muy: {FLAGS.Muy} kN-m")

    n = 1
    section_fig = []
    ir_fig = []

    while True:
        print(f"\n============== Section {n} ==============")
        main_dia = get_valid_integer("Main rebar diameter in mm : ")
        traverse_dia = get_valid_integer("Traverse rebar diameter in mm : ")

        section, ir = create_ir_diagram(main_dia, traverse_dia)

        section_fig.append(section)
        ir_fig.append(ir)

        ask = input("Any section? , Y|N : ").upper()
        if ask == "N":
            break
        else:
            n += 1

    create_html(section_fig, ir_fig)


# Call the main function
if __name__ == "__main__":
    print("Hello, world!")
    app.run(main)


"""
python app/rect.py --b=40 --h=60 --Pu=2500 --Mux=120 --Muy=45

"""
