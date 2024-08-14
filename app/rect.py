import pandas as pd

from absl import app, flags, logging
from absl.flags import FLAGS

from plot_rect import (
    get_rebar_coordinates,
    create_html,
)
from utils import (
    convert_input_to_list,
    beta_one,
    effective_depth,
    calculate_areas_in_rect,
    display_table,
)
from app.column import (
    pure_compression,
    zero_tension,
    balance,
    pure_bending,
    pure_tension,
)

## FLAGS definition
# https://stackoverflow.com/questions/69471891/clarification-regarding-abseil-library-flags

flags.DEFINE_float("fc", 23.5, "240ksc, MPa")
flags.DEFINE_integer("fy", 395, "SD40 main bar, MPa")
flags.DEFINE_integer("fv", 235, "SR24 traverse, MPa")
flags.DEFINE_float("c", 4, "concrete covering, cm")

flags.DEFINE_integer("main", 12, "main reinforcement, mm")
flags.DEFINE_integer("trav", 6, "traverse reinforcement, mm")
flags.DEFINE_float("b", 0, "width, cm")
flags.DEFINE_float("h", 0, "depth, cm")
flags.DEFINE_float("Pu", 0, "Axial force, kN")
flags.DEFINE_float("Mux", 0, "Mux, kN-m")
flags.DEFINE_float("Muy", 0, "Mux, kN-m")


# ----------------------------------------------------------------
## X-X Axis
# ----------------------------------------------------------------
def x_axis(fc, fy, Es, b, h, main_dia, traverse_dia, covering, N, df_rebars):
    print(f"\nX-X Axis")

    beta_1 = beta_one(fc)
    nuetral_axis = []
    x_ir_mux = []  # 𝜙Mn
    y_ir_mux = []  # 𝜙Pn

    Ag, Ast, An = calculate_areas_in_rect(b, h, main_dia / 10, N)  # cm2

    d, d2 = effective_depth(
        main_dia / 10, main_dia / 10, traverse_dia / 10, h, covering
    )  # cm

    ## 1-Pure Compression
    𝜙Pn, 𝜙Pn_max = pure_compression(fc, fy, Ast, An)
    y_ir_mux.append(abs(𝜙Pn))
    x_ir_mux.append(0)

    ## 2-Zero Tension
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = zero_tension(beta_1, fc, fy, Es, h, main_dia, d, df, b, rect=True)

    y_ir_mux.append(abs(𝜙Pn))
    x_ir_mux.append(𝜙Mn)
    nuetral_axis.append(c)

    ## 3-Balance
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = balance(beta_1, fc, fy, Es, h, main_dia, d, df, b, rect=True)

    y_ir_mux.append(abs(𝜙Pn))
    x_ir_mux.append(𝜙Mn)
    nuetral_axis.append(c)

    ## 4-Pure Bending
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = pure_bending(beta_1, fc, fy, Es, h, main_dia, d, d2, df, b, rect=True)

    y_ir_mux.append(0)
    x_ir_mux.append(𝜙Mn)
    nuetral_axis.append(c)

    ## 5-Pure Tension
    𝜙Pn = pure_tension(fy, Ast * 1e2)

    y_ir_mux.append(𝜙Pn)
    x_ir_mux.append(0)

    df = pd.DataFrame(
        {
            "|||": [
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
    display_table(df)

    return x_ir_mux, y_ir_mux


# ----------------------------------------------------------------
## Y-Y Axis
# ----------------------------------------------------------------
def y_axis(fc, fy, Es, b, h, main_dia, traverse_dia, covering, N, df_rebars):
    """
    With Y-Y axis
    we swapp b, h and calculate distance from top of rebar (z)
    """
    print("Y-Y Axis")

    beta_1 = beta_one(fc)

    nuetral_axis = []
    x_ir_muy = []  # 𝜙Mn
    y_ir_muy = []  # 𝜙Pn

    Ag, Ast, An = calculate_areas_in_rect(b, h, main_dia / 10, N)  # cm2

    d, d2 = effective_depth(
        main_dia / 10, main_dia / 10, traverse_dia / 10, h, covering
    )  # cm

    # Get the rebar coordinates
    # Create a new DataFrame with swapped 'x' and 'y' columns
    df_swapped = df_rebars.copy()[["x", "y"]].rename(columns={"x": "y", "y": "x"})

    # Rearrange the columns to [x, y]
    df_swapped = df_swapped[["x", "y"]]

    # Calculate distance from top
    df_swapped["z"] = h - df_swapped["y"]

    display_table(df_swapped)

    ## 1-Pure Compression
    𝜙Pn = pure_compression(fc, fy, Ast, An)
    y_ir_muy.append(abs(𝜙Pn))
    x_ir_muy.append(0)

    ## 2-Zero Tension
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = zero_tension(
        beta_1, fc, fy, Es, h, main_dia, d, df_swapped, b, rect=True
    )

    y_ir_muy.append(abs(𝜙Pn))
    x_ir_muy.append(𝜙Mn)
    nuetral_axis.append(c)

    ## 3-Balance
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = balance(beta_1, fc, fy, Es, h, main_dia, d, df_swapped, b, rect=True)

    y_ir_muy.append(abs(𝜙Pn))
    x_ir_muy.append(𝜙Mn)
    nuetral_axis.append(c)

    ## 4-Pure Bending
    df = df_rebars.copy()
    𝜙Pn, 𝜙Mn, c = pure_bending(
        beta_1, fc, fy, Es, h, main_dia, d, d2, df_swapped, b, rect=True
    )

    y_ir_muy.append(0)
    x_ir_muy.append(𝜙Mn)
    nuetral_axis.append(c)

    ## 5-Pure Tension
    𝜙Pn = pure_tension(fy, Ast * 1e2)

    y_ir_muy.append(𝜙Pn)
    x_ir_muy.append(0)

    df = pd.DataFrame(
        {
            "|||": [
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
    display_table(df)

    return x_ir_muy, y_ir_muy


# ----------------------------------------------------------------
## Main function
# ----------------------------------------------------------------
def main(argv):
    fc = FLAGS.fc
    fy = FLAGS.fy  # MPa
    Es = 200000  # MPa

    b = FLAGS.b  # width in cm
    h = FLAGS.h  # depth in cm
    covering = FLAGS.c  # covering in cm

    Pu = FLAGS.Pu  # kN
    Mux = FLAGS.Mux  # kN
    Muy = FLAGS.Muy  # kN

    main_dia = FLAGS.main  # mm
    traverse_dia = FLAGS.trav  # mm

    while True:

        bottom_layers = convert_input_to_list(
            input("Define list of bottom reinforcement for each layer, ex. 3 2 2 : ")
        )
        top_layers = convert_input_to_list(
            input("Define list of top reinforcement for each layer, ex. 3 2 : ")
        )
        middle_rebars = int(input("Define remaining middle rebars ex.4 : "))

        ask = input("Define again! Y|N :").upper()
        if ask == "Y":
            pass
        else:
            print("Goodbye!")
            break

    # Total rebars
    N = sum(bottom_layers + top_layers)

    # Get the rebar coordinates
    df_rebars = get_rebar_coordinates(
        b,
        h,
        covering,
        main_dia / 10,
        traverse_dia / 10,
        bottom_layers,
        top_layers,
        middle_rebars,
    )

    # Display rebar coordinates
    display_table(df_rebars)

    # Coordinate for IR-diagrams for Mux
    x_ir_mux, y_ir_mux = x_axis(
        fc, fy, Es, b, h, main_dia, traverse_dia, covering, N, df_rebars
    )

    # Coordinate for IR-diagrams for Muy
    # Swapp b, h
    by, hy = h, b

    x_ir_muy, y_ir_muy = y_axis(
        fc, fy, Es, by, hy, main_dia, traverse_dia, covering, N, df_rebars
    )

    # Create html file to display ploting
    create_html(
        b,
        h,
        covering,
        traverse_dia,
        main_dia,
        bottom_layers,
        top_layers,
        middle_rebars,
        x_ir_mux,
        y_ir_mux,
        x_ir_muy,
        y_ir_muy,
        Pu,
        Mux,
        Muy,
    )

    print("Please open rectangle_plot.html in your project folder")


# Call the main function
if __name__ == "__main__":
    print("Hello, world!")
    app.run(main)


"""
python app/rect.py --b=40 --h=60 --main=25 --trav=9 --Pu=2500 --Mux=120 --Muy=45

"""
