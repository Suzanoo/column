import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# Assume these are your P-M points from the existing code
phi_Pn = np.array([4361.13, 2710.06, 1386.83, 0.00, -9.93])  # kN
phi_Mn = np.array([0.00, 281.43, 292.77, 47.97, 0.00])  # kN-m

# Sort points by axial load (Pn) to ensure monotonic sequence
sorted_indices = np.argsort(phi_Pn)
phi_Pn = phi_Pn[sorted_indices]
phi_Mn = phi_Mn[sorted_indices]

# Spline interpolation
spline = CubicSpline(phi_Pn, phi_Mn)

# Generate more points for a smooth curve
phi_Pn_new = np.linspace(phi_Pn.min(), phi_Pn.max(), 50)
phi_Mn_new = spline(phi_Pn_new)

# Plot the original points and the smooth curve
plt.plot(phi_Mn, phi_Pn, "o", label="Original P-M Points")
plt.plot(phi_Mn_new, phi_Pn_new, "-", label="Smooth IR Curve")
plt.xlabel("𝜙Mn (kN)")
plt.ylabel("𝜙Pn (kN-m)")
plt.title("Interaction Ratio (IR) Diagram")
plt.legend()
plt.grid(True)
plt.show()
