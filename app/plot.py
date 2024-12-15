import plotly.graph_objects as go
from plotly.subplots import make_subplots


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

    def plot_circular_section(self, diameter, main_dia, N, c, context):
        x_outer = context["x_outer"]
        y_outer = context["y_outer"]
        x_inner = context["x_inner"]
        y_inner = context["y_inner"]
        x_traverse = context["x_traverse"]
        y_traverse = context["y_traverse"]
        x_rebar = context["x_rebar"]
        y_rebar = context["y_rebar"]

        # Create the plot
        fig = go.Figure()

        # Determine colors for rebars based on their position relative to the NA
        rebar_colors = ["red" if y > 0 else "blue" for y in y_rebar]

        # Add the solid circle for the column
        fig.add_trace(
            go.Scatter(
                x=x_outer,
                y=y_outer,
                mode="lines",
                fill="toself",
                fillcolor="lightgrey",
                line=dict(color="grey"),
                name="Column Section",
            ),
        )

        # Add the dotted circle for the covering
        fig.add_trace(
            go.Scatter(
                x=x_inner,
                y=y_inner,
                mode="lines",
                line=dict(color="green", width=2),
                name="Covering",
            ),
        )

        # Add the dotted circle for traverse
        fig.add_trace(
            go.Scatter(
                x=x_traverse,
                y=y_traverse,
                mode="lines",
                line=dict(color="green", width=2),
                name="Covering",
            ),
        )

        # Add the neutral axis (NA) as a horizontal green dotted line
        fig.add_trace(
            go.Scatter(
                x=[-diameter / 2, diameter / 2],
                y=[c - c, c - c],
                mode="lines",
                line=dict(color="green", dash="dot"),
                name="Neutral Axis",
            ),
        )

        # Add the dots for the rebars with colors based on their position relative to the NA
        fig.add_trace(
            go.Scatter(
                x=x_rebar,
                y=y_rebar,
                mode="markers+text",
                marker=dict(color=rebar_colors, size=main_dia * 5),
                text=[str(i) for i in range(1, N + 1)],
                textposition="top right",
                name="Rebars",
            ),
        )

        fig.update_layout(
            title=f"{N}-Dia{main_dia*10:.0f}mm",
            xaxis_title="X (cm)",
            yaxis_title="Y (cm)",
            showlegend=False,  # To avoid duplicate legends
            width=500,
            height=500,
        )

        # Update layout to ensure correct aspect ratio
        fig.update_xaxes(scaleanchor="y", scaleratio=1)
        fig.update_yaxes(scaleanchor="x", scaleratio=1)

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

    def create_html(self, section_fig, ir_fig, file_name):
        # Start building the HTML content
        html_content = """
        <html>
            <head>
                <title>Rectangle Plot</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
        """

        # Loop through the list of figures
        for i in range(len(section_fig)):
            # Convert each figure to HTML
            section_html = section_fig[i].to_html(
                full_html=False, include_plotlyjs=False
            )
            ir_html = ir_fig[i].to_html(full_html=False, include_plotlyjs=False)

            # Add the row for this pair of figures
            html_content += f"""
            <div style="display: flex; justify-content: space-around; margin-bottom: 30px;">
                <div style="width: 45%;">
                    <h1>Section {i + 1}</h1>
                    {section_html}
                </div>
                <div style="width: 45%;">
                    <h1>IR Diagram {i + 1}</h1>
                    {ir_html}
                </div>
            </div>
            """

        # End the HTML content
        html_content += """
            </body>
        </html>
        """

        # Write the HTML content to a file
        with open(file_name, "w") as f:
            f.write(html_content)

        print(f"Please open {file_name} in your project folder")

    def plot_combined(self, fig1, fig2):
        # Create a combined subplot with 1 row and 2 columns
        combined_fig = make_subplots(rows=1, cols=2, subplot_titles=("Mux", "Muy"))

        # Add traces from the first figure
        for trace in fig1["data"]:
            combined_fig.add_trace(trace, row=1, col=1)

        # Add traces from the second figure
        for trace in fig2["data"]:
            combined_fig.add_trace(trace, row=1, col=2)

        # Update layout for spacing and appearance
        combined_fig.update_layout(
            title_text="IR-Diagram",
            height=500,
            width=1000,
            showlegend=False,
        )

        return combined_fig
