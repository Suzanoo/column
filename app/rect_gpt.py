from section_generate import SectionGenerate
from pn_mn_calculator import PnMnCoordinateCalculator
from plot import Plot

## ----------------------------------------------------------------
section = SectionGenerate(fc=30, fv=240, fy=500, Es=200000)
context = section.rectangle(b=25, h=45)

## ----------------------------------------------------------------
force = PnMnCoordinateCalculator(
    context["materials"], context["geometry"], context["reinforcement"]
)
𝜙Pn_coords, 𝜙Mn_coords = force.pn_mn_calculator(context["df_rebars"])

## ----------------------------------------------------------------
plot = Plot()
fig = plot.plot_rc_section(context, covering=4)
fig.show()

"""
python app/rect_gpt.py
"""
