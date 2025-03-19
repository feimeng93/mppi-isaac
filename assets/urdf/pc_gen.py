import scipy.io
import trimesh

# Step 1: Load the .mat file
mat_data = scipy.io.loadmat('/home/hkcrc/mf_code/mppi-isaac/assets/urdf/heart2/pcd/heart2_contour_data/vertices_faces_3.mat')

# Extract vertices and faces
vertices = mat_data['vertices_faces']['vertices'][0][0]
faces = mat_data['vertices_faces']['faces'][0][0] - 1  # Convert to 0-based indexing

# Step 2: Create a mesh object
mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

# Step 3: Export to STL
mesh.export('/home/hkcrc/mf_code/mppi-isaac/assets/urdf/heart2/heart2.stl')

print("STL file saved as 'output.stl'")