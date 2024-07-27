import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Plot 1 circular section
def circular_section(
    dia,
    main_dia,
    N,
    c,
    x_outer,
    y_outer,
    x_inner,
    y_inner,
    x_rebar,
    y_rebar,
):

    # Create the plot
    fig = go.Figure()

    # Determine colors for rebars based on their position relative to the NA
    rebar_colors = ["red" if y > c else "black" for y in y_rebar]

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
            line=dict(color="black", dash="dot"),
            name="Covering",
        ),
    )

    # Add the neutral axis (NA) as a horizontal green dotted line
    fig.add_trace(
        go.Scatter(
            x=[-dia / 2, dia / 2],
            y=[c, c],
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
            marker=dict(color=rebar_colors, size=main_dia * 7),
            text=[str(i) for i in range(1, N + 1)],
            textposition="top right",
            name="Rebars",
        ),
    )

    # Update layout to ensure correct aspect ratio
    fig.update_xaxes(scaleanchor="y", scaleratio=1)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    # Show the plot
    fig.show()


# Plot IR-Diagram
def IR_diagram_plot(x, y, Pu, Mu):
    # Create the plot
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

    # Update the layout
    fig.update_layout(
        title="IR Diagram",
        xaxis_title="𝜙Mn, kN-m",
        yaxis_title="𝜙Pn, kN",
        legend_title="Legend",
        width=800,
        height=800,
        # xaxis=dict(range=[0, max(x) * 1.1]),  # Ensure x-axis starts at 0
        # yaxis=dict(range=[0, max(y) * 1.1]),  # Ensure y-axis starts at 0
    )

    # Show the plot
    fig.show()


# Plot circular section in subplot
def circular_section_plot(
    fig,
    row,
    col,
    dia,
    main_dia,
    N,
    c,
    x_outer,
    y_outer,
    x_inner,
    y_inner,
    x_rebar,
    y_rebar,
):

    # Determine colors for rebars based on their position relative to the NA
    rebar_colors = ["red" if y > c else "black" for y in y_rebar]

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
        row=row,
        col=col,
    )

    # Add the dotted circle for the covering
    fig.add_trace(
        go.Scatter(
            x=x_inner,
            y=y_inner,
            mode="lines",
            line=dict(color="black", dash="dot"),
            name="Covering",
        ),
        row=row,
        col=col,
    )

    # Add the neutral axis (NA) as a horizontal green dotted line
    fig.add_trace(
        go.Scatter(
            x=[-dia / 2, dia / 2],
            y=[c, c],
            mode="lines",
            line=dict(color="green", dash="dot"),
            name="Neutral Axis",
        ),
        row=row,
        col=col,
    )

    # Add the dots for the rebars with colors based on their position relative to the NA
    fig.add_trace(
        go.Scatter(
            x=x_rebar,
            y=y_rebar,
            mode="markers+text",
            marker=dict(color=rebar_colors, size=main_dia * 7),
            text=[str(i) for i in range(1, N + 1)],
            textposition="top right",
            name="Rebars",
        ),
        row=row,
        col=col,
    )

    # Update layout to ensure correct aspect ratio
    fig.update_xaxes(scaleanchor="y", scaleratio=1, row=row, col=col)
    fig.update_yaxes(scaleanchor="x", scaleratio=1, row=row, col=col)

    return fig


# Multiple plot circular section with subplot
def plot_multiple_sections(dia, main_dia, N, neutral_axis, data, rows, cols):
    # Initialize the subplot figure
    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=[f"Section {i+1}" for i in range(len(neutral_axis))],
    )

    # Iterate over the list of neutral axis distances and plot each section
    for i, c in enumerate(neutral_axis):
        row = i // cols + 1
        col = i % cols + 1
        fig = circular_section_plot(
            fig,
            row,
            col,
            dia,
            main_dia,
            N,
            -(c - dia / 2),
            data["x_outer"],
            data["y_outer"],
            data["x_inner"],
            data["y_inner"],
            data["x_rebar"],
            data["y_rebar"],
        )

    # Update layout of the combined figure
    fig.update_layout(
        title="Column Sections",
        xaxis_title="X (cm)",
        yaxis_title="Y (cm)",
        showlegend=False,  # To avoid duplicate legends
        width=800,
        height=800,
    )

    # Show the combined figure
    fig.show()
