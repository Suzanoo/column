import plotly.graph_objects as go

from rebar import Rebar


class Plot:
    def __init__(self):
        self.rebar = Rebar()

    def plot_rc_section(self, context, covering):

        fig = go.Figure()

        b = context["geometry"].b
        h = context["geometry"].h
        main_dia = context["reinforcement"].main_dia / 10  # Convert mm to cm
        traverse_dia = context["reinforcement"].traverse_dia / 10  # Convert mm to cm

        bottom_layers = context["bottom_layers"]
        top_layers = context["top_layers"]
        middle_rebars = context["middle_rebars"]

        # Draw the concrete section
        fig.add_shape(
            type="rect",
            x0=0,
            y0=0,
            x1=b,
            y1=h,
            line=dict(color="gray", width=3),
            fillcolor="lightgray",
        )

        # Draw the concrete cover
        fig.add_shape(
            type="rect",
            x0=covering,
            y0=covering,
            x1=b - covering,
            y1=h - covering,
            line=dict(color="green", width=2),
        )

        # Draw the traverse
        fig.add_shape(
            type="rect",
            x0=covering + traverse_dia,
            y0=covering + traverse_dia,
            x1=b - covering - traverse_dia,
            y1=h - covering - traverse_dia,
            line=dict(color="green", width=2),
        )

        # Calculate positions of top reinforcement layers
        layer_spacing = 2 * main_dia
        y_top_layers = [
            h - covering - (i + 0.5) * layer_spacing for i in range(len(top_layers))
        ]

        for y, num_bars in zip(y_top_layers, top_layers):
            x_positions = self.rebar.calculate_rebar_positions(
                covering,
                b,
                num_bars,
                main_dia,
                traverse_dia,
            )
            for x in x_positions:
                fig.add_shape(
                    type="circle",
                    x0=x - main_dia / 2,
                    y0=y - main_dia / 2,
                    x1=x + main_dia / 2,
                    y1=y + main_dia / 2,
                    line=dict(color="blue"),
                    fillcolor="blue",
                )

        # Calculate positions of bottom reinforcement layers
        y_bottom_layers = [
            covering + (i + 0.5) * layer_spacing for i in range(len(bottom_layers))
        ]

        for y, num_bars in zip(y_bottom_layers, bottom_layers):
            x_positions = self.rebar.calculate_rebar_positions(
                covering,
                b,
                num_bars,
                main_dia,
                traverse_dia,
            )
            for x in x_positions:
                fig.add_shape(
                    type="circle",
                    x0=x - main_dia / 2,
                    y0=y - main_dia / 2,
                    x1=x + main_dia / 2,
                    y1=y + main_dia / 2,
                    line=dict(color="blue"),
                    fillcolor="blue",
                )

        # Calculate positions of middle reinforcement layers
        if middle_rebars > 0:
            n = middle_rebars // 2
            d_middle = min(y_top_layers) - max(y_bottom_layers)
            s = d_middle / (n + 1)

            for i in range(1, n + 1):
                y_position = max(y_bottom_layers) + s * i
                fig.add_shape(
                    type="circle",
                    x0=covering + traverse_dia,
                    y0=y_position - main_dia / 2,
                    x1=covering + traverse_dia + main_dia,
                    y1=y_position + main_dia / 2,
                    line=dict(color="blue"),
                    fillcolor="blue",
                )
                fig.add_shape(
                    type="circle",
                    x0=b - covering - traverse_dia - main_dia,
                    y0=y_position - main_dia / 2,
                    x1=b - covering - traverse_dia,
                    y1=y_position + main_dia / 2,
                    line=dict(color="blue"),
                    fillcolor="blue",
                )

        # Set axis properties to ensure equal scale
        fig.update_xaxes(range=[-5, b + 5], scaleratio=1, zeroline=False)
        fig.update_yaxes(range=[-5, h + 5], scaleratio=1, zeroline=False)
        fig.update_layout(
            title="RC Beam Section",
            xaxis_title="Width (cm)",
            yaxis_title="Depth (cm)",
            height=600,
            width=600,
            yaxis=dict(scaleanchor="x", scaleratio=1),
        )

        return fig

    def IR_diagram(self, x, y, Pu, Mu, title):

        fig = go.Figure()
        # Add the scatter plot
        fig.add_trace(
            go.Scatter(
                x=x, y=y, mode="markers+lines", name="[𝜙Mn, 𝜙Pn]", marker=dict(size=12)
            ),
        )

        # Add the additional point (P, M)
        fig.add_trace(
            go.Scatter(
                x=[Mu],
                y=[Pu],
                mode="markers",
                name="Mu, Pu",
                marker=dict(size=12, color="red"),  # Larger and different color marker
            ),
        )

        fig.update_xaxes(title_text="𝜙Mn, kN-m")
        fig.update_yaxes(title_text="𝜙Pn, kN")

        # Update the layout
        fig.update_layout(
            title=title,
            legend_title="Legend",
            width=1200,
            height=900 * 2 / 3,
        )

        return fig
