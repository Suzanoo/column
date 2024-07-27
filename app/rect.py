import pandas as pd

from plot_rect import (
    get_rebar_coordinates,
    create_html,
)
from utils import beta_one, effective_depth, calculate_areas_in_rect, display_table
from PM import pure_compression, zero_tension, balance, pure_bending, pure_tension


# Example usage
b = 50  # width in cm
h = 50  # depth in cm
covering = 4.5  # covering in cm

main_dia = 16  # mm
traverse_dia = 9  # mm
bottom_layers = [3]
top_layers = [3]

fc = 24
fy = 390  # MPa
Es = 200000  # MPa

Pu = 2500  # kN
Mux = 54  # kN
Muy = 25  # kN

beta_1 = beta_one(fc)
N = sum(bottom_layers + top_layers)
# ----------------------------------------------------------------
## X-X Axis
# ----------------------------------------------------------------
print("X-X Axis")

nuetral_axis = []
x_ir_mux = []  # 𝜙Mn
y_ir_mux = []  # 𝜙Pn

Ag, Ast, An = calculate_areas_in_rect(b, h, main_dia / 10, N)  # cm2
d, d2 = effective_depth(
    main_dia / 10, main_dia / 10, traverse_dia / 10, h, covering
)  # cm

# Get the rebar coordinates
df_rebars = get_rebar_coordinates(
    b, h, covering, main_dia / 10, bottom_layers, top_layers
)

display_table(df_rebars)


## 1-Pure Compression
𝜙Pn = pure_compression(fc, fy, Ast, An)
y_ir_mux.append(abs(𝜙Pn))
x_ir_mux.append(0)


## 2-Zero Tension
df = df_rebars.copy()
𝜙Pn, 𝜙Mn, c = zero_tension(beta_1, fc, fy, Es, h, main_dia, d, df, b, rect=True)

y_ir_mux.append(abs(𝜙Pn))
x_ir_mux.append(𝜙Mn)
nuetral_axis.append(c)


## 3-Balance
df = df_rebars.copy()
𝜙Pn, 𝜙Mn, c = balance(beta_1, fc, fy, Es, h, main_dia, d, df, b, rect=True)

y_ir_mux.append(abs(𝜙Pn))
x_ir_mux.append(𝜙Mn)
nuetral_axis.append(c)


## 4-Pure Bending
df = df_rebars.copy()
𝜙Pn, 𝜙Mn, c = pure_bending(beta_1, fc, fy, Es, h, main_dia, d, d2, df, b, rect=True)

y_ir_mux.append(0)
x_ir_mux.append(𝜙Mn)
nuetral_axis.append(c)


## 5-Pure Tension
𝜙Pn = pure_tension(fy, Ast * 1e2)

y_ir_mux.append(𝜙Pn)
x_ir_mux.append(0)

df = pd.DataFrame(
    {
        "|||": [
            "Pure Compression",
            "Zero Tension",
            "Balance",
            "Pure Bending",
            "Pure Tension",
        ],
        "𝜙Pn, kN": y_ir_mux,
        "𝜙Mn, kN-m": x_ir_mux,
    }
)
display_table(df)

# ----------------------------------------------------------------
## Y-Y Axis
# ----------------------------------------------------------------
"""
With Y-Y axis
we swapp b, h and calculate distance from top of rebar (z)
next we need list of top and bottom 
user see the table and input
"""
print("Y-Y Axis")

nuetral_axis = []
x_ir_muy = []  # 𝜙Mn
y_ir_muy = []  # 𝜙Pn

b, h = h, b
d, d2 = effective_depth(
    main_dia / 10, main_dia / 10, traverse_dia / 10, h, covering
)  # cm

# Get the rebar coordinates
# Create a new DataFrame with swapped 'x' and 'y' columns
df_swapped = df_rebars.copy()[["x", "y"]].rename(columns={"x": "y", "y": "x"})

# Rearrange the columns to [x, y]
df_swapped = df_swapped[["x", "y"]]

# Calculate distance from top
df_swapped["z"] = h - df_swapped["y"]

display_table(df_swapped)


## 1-Pure Compression
𝜙Pn = pure_compression(fc, fy, Ast, An)
y_ir_muy.append(abs(𝜙Pn))
x_ir_muy.append(0)


## 2-Zero Tension
df = df_rebars.copy()
𝜙Pn, 𝜙Mn, c = zero_tension(beta_1, fc, fy, Es, h, main_dia, d, df_swapped, b, rect=True)

y_ir_muy.append(abs(𝜙Pn))
x_ir_muy.append(𝜙Mn)
nuetral_axis.append(c)


## 3-Balance
df = df_rebars.copy()
𝜙Pn, 𝜙Mn, c = balance(beta_1, fc, fy, Es, h, main_dia, d, df_swapped, b, rect=True)

y_ir_muy.append(abs(𝜙Pn))
x_ir_muy.append(𝜙Mn)
nuetral_axis.append(c)


## 4-Pure Bending
df = df_rebars.copy()
𝜙Pn, 𝜙Mn, c = pure_bending(
    beta_1, fc, fy, Es, h, main_dia, d, d2, df_swapped, b, rect=True
)

y_ir_muy.append(0)
x_ir_muy.append(𝜙Mn)
nuetral_axis.append(c)


## 5-Pure Tension
𝜙Pn = pure_tension(fy, Ast * 1e2)

y_ir_muy.append(𝜙Pn)
x_ir_muy.append(0)

df = pd.DataFrame(
    {
        "|||": [
            "Pure Compression",
            "Zero Tension",
            "Balance",
            "Pure Bending",
            "Pure Tension",
        ],
        "𝜙Pn, kN": y_ir_muy,
        "𝜙Mn, kN-m": x_ir_muy,
    }
)
display_table(df)


# ----------------------------------------------------------------
## # Plot
# ----------------------------------------------------------------
# Back to X-axis
b, h = h, b

# Create html file to display ploting
create_html(
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


"""
python app/rect.py
"""
