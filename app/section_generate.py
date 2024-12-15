import numpy as np
import pandas as pd

from column import (
    MaterialProperties,
    SectionGeometry,
    Reinforcement,
)

from rebar import Rebar
from utils import display_table, get_valid_integer


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
        geometry = SectionGeometry()
        geometry.rectangle(b=b, h=h)

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

    def circular(self, diameter, covering):
        # Step 1: Define material properties
        materials = MaterialProperties(self.fc, self.fv, self.fy, self.Es)

        # Step 2: Define section geometry
        geometry = SectionGeometry()
        geometry.circular(diameter)

        # Step 3: Define reinforcement details
        rebar = Rebar()
        main_dia, As = rebar.rebar_selected("Main rebar diameter in mm : ")
        traverse_dia, Av = rebar.rebar_selected("Traverse rebar diameter in mm : ")
        N = get_valid_integer("Numbers of Main rebars : ")

        # Reinforcement object
        reinforcement = Reinforcement(main_dia, traverse_dia, N)

        # Calculate the inner diameter
        inner_dia = (
            diameter - 2 * covering - main_dia / 10 - traverse_dia / 10
        )  # for main reinforcements
        inner_dia2 = diameter - 2 * covering  # for covering
        inner_dia3 = diameter - 2 * covering - 2 * traverse_dia / 10  # for traverse

        # Create the solid circle for the column section
        theta = np.linspace(0, 2 * np.pi, 100)
        x_outer = (diameter / 2) * np.cos(theta)
        y_outer = (diameter / 2) * np.sin(theta)

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
        distance_from_top = (diameter / 2) - y_rebar

        # Create a DataFrame of rebars
        df_rebars = pd.DataFrame(
            {
                "No": list(range(1, N + 1)),
                "x": x_rebar,
                "y": y_rebar,
                "z": distance_from_top,
            }
        )
        print("[INFO] : Rebars position:")
        display_table(df_rebars)

        force_context = {
            "materials": materials,
            "geometry": geometry,
            "reinforcement": reinforcement,
            "df_rebars": df_rebars,
        }

        plot_context = {
            "x_outer": x_outer,
            "y_outer": y_outer,
            "x_inner": x_inner,
            "y_inner": y_inner,
            "x_traverse": x_traverse,
            "y_traverse": y_traverse,
            "x_rebar": x_rebar,
            "y_rebar": y_rebar,
        }

        return force_context, plot_context
