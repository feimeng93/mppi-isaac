import numpy as np
import pyvista as pv

# Define the implicit function for the heart
def heart_implicit(x, y, z):
    return ((5*x)**2 + (9/4)*(5*y)**2 + (5*z)**2 - 1)**3 - (5*x)**2 * (5*z)**3 - (9/80) * (5*y)**2 * (5*z)**3

# Create a grid of points
x = np.linspace(-1.5, 1.5, 250)
y = np.linspace(-1.5, 1.5, 250)
z = np.linspace(-1.5, 1.5, 250)
x, y, z = np.meshgrid(x, y, z)
grid = pv.StructuredGrid(x, y, z)

# Evaluate the implicit function at each point
values = heart_implicit(x, y, z).flatten()

# Extract the surface where the implicit function equals zero
heart_mesh = grid.contour([0], values)

# Save the mesh as an STL file
heart_mesh.save("heart.stl")