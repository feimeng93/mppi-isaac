import numpy as np
import pyvista as pv
import os


obs = 'heart2'

def generate_urdf_files(template_path: str, output_dir: str, num_files: int):
    """
    Generate URDF files with modified filenames.

    :param template_path: Path to the template URDF file.
    :param output_dir: Directory to save the generated URDF files.
    :param num_files: Number of URDF files to generate.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(template_path, 'r') as template_file:
        template_content = template_file.read()

    for i in range(num_files):
        modified_content = template_content.replace('heart.stl', f'{obs}_{i}.stl')
        output_path = os.path.join(output_dir, f'{obs}_{i}.urdf')
        with open(output_path, 'w') as output_file:
            output_file.write(modified_content)

def generate_stl_files(output_dir: str, num_files: int):
    """
    Generate STL files for the heart model.

    :param output_dir: Directory to save the generated STL files.
    :param num_files: Number of STL files to generate.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(num_files):
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
        stl_filename = os.path.join(output_dir, f'{obs}_{i}.stl')
        heart_mesh.save(stl_filename)
# Example usage
template_path = f'./{obs}/heart.urdf' # heart1 / heart2
output_dir = f'./{obs}/uncertain'
num_files = 500

generate_urdf_files(template_path, output_dir, num_files)
generate_stl_files(output_dir, num_files)