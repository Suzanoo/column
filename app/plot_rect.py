import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd

from utils import display_table


def calculate_rebar_positions(c, b, N):
    if N == 1:
        return [c + (b - 2 * c) / 2]
    elif N == 2:
        return [c, b - c]
    else:
        positions = [c + i * (b - 2 * c) / (N - 1) for i in range(N)]
        return positions


def get_rebar_coordinates(b, h, c, main_dia, bottom_layers, top_layers):
    rebar_data = []

    # Calculate positions of bottom reinforcement layers
    layer_spacing = 2 * main_dia
    y_bottom_layers = [c + (i + 0.5) * layer_spacing for i in range(len(bottom_layers))]

    for y, num_bars in zip(y_bottom_layers, bottom_layers):
        x_positions = calculate_rebar_positions(c, b, num_bars)
        for x in x_positions:
            z = h - y
            rebar_data.append({"x": x, "y": y, "z": z})

    # Calculate positions of top reinforcement layers
    y_top_layers = [h - c - (i + 0.5) * layer_spacing for i in range(len(top_layers))]

    for y, num_bars in zip(y_top_layers, top_layers):
        x_positions = calculate_rebar_positions(c, b, num_bars)
        for x in x_positions:
            z = h - y
            rebar_data.append({"x": x, "y": y, "z": z})

    return pd.DataFrame(rebar_data)


def plot_rc_section(fig, b, d, c, travesre_dia, main_dia, bottom_layers, top_layers):
    # fig = go.Figure()

    # Draw the concrete section
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=b,
        y1=d,
        line=dict(color="gray", width=3),
        fillcolor="lightgray",
    )

    # Draw the concrete cover
    fig.add_shape(
        type="rect",
        x0=c - main_dia / 2,
        y0=c + main_dia / 2,
        x1=b - c + main_dia / 2,
        y1=d - c - main_dia / 2,
        line=dict(color="red", width=2, dash="dot"),
    )

    # Calculate positions of bottom reinforcement layers
    layer_spacing = 2 * main_dia
    y_bottom_layers = [c + (i + 0.5) * layer_spacing for i in range(len(bottom_layers))]

    for y, num_bars in zip(y_bottom_layers, bottom_layers):
        x_positions = calculate_rebar_positions(c, b, num_bars)
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

    # Calculate positions of top reinforcement layers
    y_top_layers = [d - c - (i + 0.5) * layer_spacing for i in range(len(top_layers))]

    for y, num_bars in zip(y_top_layers, top_layers):
        x_positions = calculate_rebar_positions(c, b, num_bars)
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

    # Set axis properties to ensure equal scale
    fig.update_xaxes(range=[-5, b + 5], scaleratio=1, zeroline=False)
    fig.update_yaxes(range=[-5, d + 5], scaleratio=1, zeroline=False)
    fig.update_layout(
        title="RC Beam/Column Section",
        xaxis_title="Width (cm)",
        yaxis_title="Depth (cm)",
        height=600,
        width=600,
        yaxis=dict(scaleanchor="x", scaleratio=1),
    )

    # fig.show()
    return fig


def IR_diagram(fig, row, col, x, y, Pu, Mu, title):

    # Add the scatter plot
    fig.add_trace(
        go.Scatter(
            x=x, y=y, mode="markers+lines", name="[𝜙Mn, 𝜙Pn]", marker=dict(size=12)
        ),
        row=row,
        col=col,
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
        row=row,
        col=col,
    )

    fig.update_xaxes(title_text="𝜙Mn, kN-m", row=row, col=col)
    fig.update_yaxes(title_text="𝜙Pn, kN", row=row, col=col)

    # Update the layout
    fig.update_layout(
        title=title,
        legend_title="Legend",
        width=800,
        height=800 * 2 / 3,
    )

    return fig


def plot_IR_diagram(x_ir_mux, y_ir_mux, x_ir_muy, y_ir_muy, Pu, Mux, Muy):
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("IR Diagram (Mux)", "IR Diagram (Muy)"),
        shared_yaxes=True,
    )

    fig = IR_diagram(
        fig,
        row=1,
        col=1,
        x=x_ir_mux,
        y=y_ir_mux,
        Pu=Pu,
        Mu=Mux,
        title="IR Diagram",
    )

    fig = IR_diagram(
        fig,
        row=1,
        col=2,
        x=x_ir_muy,
        y=y_ir_muy,
        Pu=Pu,
        Mu=Muy,
        title="IR Diagram",
    )

    fig.update_layout(showlegend=True)

    # fig.show()
    return fig


def create_plot(
    b,
    h,
    covering,
    traverse_dia,
    main_dia,
    bottom_layers,
    top_layers,
    x_ir_mux,
    y_ir_mux,
    x_ir_muy,
    y_ir_muy,
    Pu,
    Mux,
    Muy,
):
    section_fig = go.Figure()
    section_fig = plot_rc_section(
        section_fig,
        b,
        h,
        covering,
        traverse_dia / 10,
        main_dia / 10,
        bottom_layers,
        top_layers,
    )

    ir_fig = plot_IR_diagram(x_ir_mux, y_ir_mux, x_ir_muy, y_ir_muy, Pu, Mux, Muy)

    return section_fig, ir_fig


def create_html(
    b,
    h,
    covering,
    traverse_dia,
    main_dia,
    bottom_layers,
    top_layers,
    x_ir_mux,
    y_ir_mux,
    x_ir_muy,
    y_ir_muy,
    Pu,
    Mux,
    Muy,
):

    section_fig, ir_fig = create_plot(
        b,
        h,
        covering,
        traverse_dia,
        main_dia,
        bottom_layers,
        top_layers,
        x_ir_mux,
        y_ir_mux,
        x_ir_muy,
        y_ir_muy,
        Pu,
        Mux,
        Muy,
    )

    # Save each plot to a string
    section_html = section_fig.to_html(full_html=False, include_plotlyjs="cdn")
    ir_html = ir_fig.to_html(full_html=False, include_plotlyjs="cdn")

    # Combine both plots into one HTML file
    with open("combined_plot.html", "w") as f:
        f.write(
            f"""
        <html>
            <head>
                <title>Combined Plot</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
                <h1>Section Plot</h1>
                {section_html}
                <h1>IR Diagram</h1>
                {ir_html}
            </body>
        </html>
        """
        )
