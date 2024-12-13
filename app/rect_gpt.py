from section_generate import SectionGenerate
from pm_calculator import PnMnCalculator


section = SectionGenerate(fc=30, fv=240, fy=500, Es=200000)
materials, geometry, reinforcement, df_rebars = section.rectangle(b=25, h=45)

force = PnMnCalculator(materials, geometry, reinforcement)
𝜙Pn, 𝜙Mn = force.pn_mn_calculator(df_rebars)
