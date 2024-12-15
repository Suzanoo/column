from absl import app, flags
from absl.flags import FLAGS

from section_generate import SectionGenerate
from pn_mn_calculator import PnMnCoordinateCalculator
from plot import Plot

from utils import display_table

flags.DEFINE_float("fc", 23.5, "240ksc, MPa")
flags.DEFINE_integer("fy", 395, "SD40 main bar, MPa")
flags.DEFINE_integer("fv", 235, "SR24 traverse, MPa")
flags.DEFINE_integer("Es", 200000, "Young's modulus ,MPa")
flags.DEFINE_float("c", 4, "concrete covering, cm")

flags.DEFINE_float("b", 0, "width, cm")
flags.DEFINE_float("h", 0, "depth, cm")
flags.DEFINE_float("Pu", 0, "Axial force, kN")
flags.DEFINE_float("Mux", 0, "Mux, kN-m")
flags.DEFINE_float("Muy", 0, "Mux, kN-m")


def main(argv):
    print("====================== Rectangular Column Design ======================")
    print("[INFO] Information : ")
    print(
        f"[Material] - fc: {FLAGS.fc} MPa, fv: {FLAGS.fv} MPa, fy: {FLAGS.fy} MPa, Es: {FLAGS.Es} MP"
    )
    print(f"[Geometry] - bxh : {FLAGS.b} x {FLAGS.h} cm")
    print(f"[Loads] - Pu: {FLAGS.Pu} kN, Mux: {FLAGS.Mux} kN-m, Muy: {FLAGS.Muy} kN-m")

    # Create plot object
    plot = Plot()

    # Placefholder
    n, sections_placholder, ir_placeholder = 1, [], []

    # Create section object
    section = SectionGenerate(FLAGS.fc, FLAGS.fv, FLAGS.fy, FLAGS.Es)

    # Generate column section
    context = section.rectangle(FLAGS.b, FLAGS.h)

    ## ----------------------------------------------------------------
    print("==================== Mux ===================")
    # Calculate column strength
    force = PnMnCoordinateCalculator(
        context["materials"], context["geometry"], context["reinforcement"]
    )
    𝜙Pn_coords, 𝜙Mn_coords = force.compute_pn_mn(context["df_rebars"])

    # Generate section figure and IR diagram figure
    section_fig = plot.plot_rc_section(context, FLAGS.c)
    irx_fig = plot.IR_diagram(𝜙Mn_coords, 𝜙Pn_coords, FLAGS.Pu, FLAGS.Mux, "IR-Diagram")

    ## ----------------------------------------------------------------
    print("==================== Muy ===================")
    # Swapped geometry
    context["geometry"].b, context["geometry"].h = (
        context["geometry"].h,
        context["geometry"].b,
    )

    # Swapped rebars coordinates 'x' and 'y' in df
    df_swapped = (
        context["df_rebars"].copy()[["x", "y"]].rename(columns={"x": "y", "y": "x"})
    )

    # Rearrange the columns to [x, y]
    df_swapped = df_swapped[["x", "y"]]

    # Calculate distance from top, z
    df_swapped["z"] = FLAGS.b - df_swapped["y"]
    display_table(df_swapped)

    # Calculate column strength
    force = PnMnCoordinateCalculator(
        context["materials"], context["geometry"], context["reinforcement"]
    )
    𝜙Pn_coords, 𝜙Mn_coords = force.compute_pn_mn(df_swapped)

    # Generate section figure and IR diagram figure
    iry_fig = plot.IR_diagram(𝜙Mn_coords, 𝜙Pn_coords, FLAGS.Pu, FLAGS.Muy, "IR-Diagram")
    combined_fig = plot.plot_combined(irx_fig, iry_fig)

    # Collect into placefholder
    sections_placholder.append(section_fig)
    ir_placeholder.append(combined_fig)

    plot.create_html(
        sections_placholder, ir_placeholder, file_name="rectangle_plot.html"
    )


# Call the main function
if __name__ == "__main__":
    print("Hello, world!")
    app.run(main)


"""
python app/rectangle.py --b=25 --h=25 --Pu=450 --Mux=15 --Muy=10
"""
