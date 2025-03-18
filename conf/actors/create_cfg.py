import os
import yaml
from typing import List

class QuotedString(str):
    pass

def quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(QuotedString, quoted_presenter)

def generate_actor_yaml_files(actor_name: str, num_files: int, output_dir: str, init_pos_val: List[float]):
    """
    Generate YAML files for actor configurations.

    :param actor_name: Name of the actor.
    :param num_files: Number of YAML files to generate.
    :param output_dir: Directory to save the generated YAML files.
    :param init_pos_val: Initial position values.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(num_files):
        actor_cfg = {
            'type': 'nonconvex_mesh',  # or 'box', 'sphere', etc.
            'name': f'{actor_name}_{i}',
            'urdf_file': QuotedString(f"{actor_name}/uncertain/{actor_name}_{i}.urdf"),
            'flip_visual': False,
            'collision': True,
            'gravity': False,
            'init_pos': init_pos_val,
            'fixed': True,
            'handle': 'None',
            'color': [255, 0, 0],
        }

        file_path = os.path.join(output_dir, f'{actor_name}_{i}.yaml')
        with open(file_path, 'w') as yaml_file:
            yaml.dump(actor_cfg, yaml_file, default_flow_style=True, sort_keys=False)

# Example usage
generate_actor_yaml_files('heart1', 500, './heart1', [0.0, 0.3, 0.85])