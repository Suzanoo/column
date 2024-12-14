from column_gpt import (
    MaterialProperties,
    SectionGeometry,
    Reinforcement,
)

from rebar import Rebar
from utils import display_table


class SectionGenerate:
    def __init__(self, fc, fv, fy, Es):
        self.fc = fc  # Concrete compressive strength (MPa)
        self.fv = fv  # Steel yield strength (MPa) of round bar
        self.fy = fy  # Steel yield strength (MPa) of deform bar
        self.Es = Es  # Steel elastic modulus (MPa)

    def rectangle(self, b, h):
        # Step 1: Define material properties
        materials = MaterialProperties(self.fc, self.fv, self.fy, self.Es)

        # Step 2: Define section geometry
        geometry = SectionGeometry(b=b, h=h)

        # Step 3: Define reinforcement details
        rebar = Rebar()
        main_dia, As = rebar.rebar_selected("Main rebar diameter in mm : ")
        traverse_dia, Av = rebar.rebar_selected("Traverse rebar diameter in mm : ")

        bottom_layers, top_layers, middle_rebars = rebar.rebar_laying()

        # Total rebars
        total_rebars = sum(bottom_layers + top_layers) + middle_rebars

        # Reinforcement object
        reinforcement = Reinforcement(main_dia, traverse_dia, total_rebars)

        # Get the rebar coordinates
        df_rebars = rebar.get_rebar_coordinates(
            geometry.b,
            geometry.h,
            4.5,
            reinforcement.main_dia / 10,
            reinforcement.traverse_dia / 10,
            bottom_layers,
            top_layers,
            middle_rebars,
        )

        display_table(df_rebars)

        context = {
            "materials": materials,
            "geometry": geometry,
            "reinforcement": reinforcement,
            "bottom_layers": bottom_layers,
            "top_layers": top_layers,
            "middle_rebars": middle_rebars,
            "df_rebars": df_rebars,
        }

        return context
