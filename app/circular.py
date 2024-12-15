import numpy as np

from absl import app, flags
from absl.flags import FLAGS

from section_generate import SectionGenerate
from pn_mn_calculator import PnMnCoordinateCalculator
from plot import Plot


flags.DEFINE_float("fc", 23.5, "240ksc, MPa")
flags.DEFINE_integer("fy", 395, "SD40 main bar, MPa")
flags.DEFINE_integer("fv", 235, "SR24 traverse, MPa")
flags.DEFINE_integer("Es", 200000, "Young's modulus ,MPa")
flags.DEFINE_float("c", 4, "concrete covering, cm")

flags.DEFINE_float("dia", 0, "diameter, cm")
flags.DEFINE_float("Pu", 0, "Axial force, kN")
flags.DEFINE_float("Mux", 0, "Mux, kN-m")
flags.DEFINE_float("Muy", 0, "Mux, kN-m")


def main(argv):
    print("====================== Rectangular Column Design ======================")
    print("[INFO] Information : ")
    print(
        f"[Material] - fc: {FLAGS.fc} MPa, fv: {FLAGS.fv} MPa, fy: {FLAGS.fy} MPa, Es: {FLAGS.Es} MP"
    )
    print(f"[Geometry] - Diameter : {FLAGS.dia} cm")
    print(f"[Loads] - Pu: {FLAGS.Pu} kN, Mux: {FLAGS.Mux} kN-m, Muy: {FLAGS.Muy} kN-m")

    # Create column object
    section = SectionGenerate(FLAGS.fc, FLAGS.fv, FLAGS.fy, FLAGS.Es)

    # Generate column section
    force_context, plot_context = section.circular(FLAGS.dia, FLAGS.c)

    # Calculate column strength
    force = PnMnCoordinateCalculator(
        force_context["materials"],
        force_context["geometry"],
        force_context["reinforcement"],
    )
    𝜙Pn_coords, 𝜙Mn_coords = force.compute_pn_mn(force_context["df_rebars"])

    # Generate section figure and IR diagram figure
    plot = Plot()
    section_fig = plot.plot_circular_section(
        FLAGS.dia,
        force_context["reinforcement"].main_dia / 10,  # Convert mm to cm
        force_context["reinforcement"].N,
        FLAGS.dia / 2,
        plot_context,
    )

    Mu = np.sqrt(FLAGS.Mux * FLAGS.Mux + FLAGS.Muy * FLAGS.Muy)

    ir_fig = plot.IR_diagram(𝜙Mn_coords, 𝜙Pn_coords, FLAGS.Pu, Mu, "IR-Diagram")

    section_fig.show()
    ir_fig.show()


# Call the main function
if __name__ == "__main__":
    print("Hello, world!")
    app.run(main)


"""
python app/circular.py --dia=30 --Pu=450 --Mux=15 --Muy=10
"""
