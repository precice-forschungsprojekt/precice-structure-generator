import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
import yaml
import pytest

from FileGenerator import FileGenerator

class TopologyCouplingTest:
    def __init__(self):
        self.template_config = Path('controller_utils/examples/1/topology.yaml')
        self.output_dir = Path('tests/generation-tests/topology_coupling_tests')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _create_temp_config(self, topology_type):
        # Validate topology type
        if topology_type not in ['strong', 'weak']:
            raise ValueError(f"Invalid topology type: {topology_type}. Must be 'strong' or 'weak'.")
        
        # Create a unique filename for each topology type
        output_filename = self.output_dir / f'topology_{topology_type}.yaml'
        
        # Load the original topology
        with open(self.template_config, 'r') as f:
            topology_config = yaml.safe_load(f)
        
        # Replace exchange types
        for exchange in topology_config['exchanges']:
            exchange['type'] = topology_type
        
        # Save modified topology
        with open(output_filename, 'w') as f:
            yaml.dump(topology_config, f)
        
        # Generate config using FileGenerator
        file_generator = FileGenerator(
            input_file=output_filename, 
            output_path=self.output_dir
        )
        file_generator._generate_precice_config()
        
        # Return the generated XML config path
        return self.output_dir / '_generated' / 'precice-config.xml'

    def _check_coupling_type(self, config_file, expected_type):
        # Read and print the XML content for debugging
        with open(config_file, 'r') as f:
            xml_content = f.read()
            print(f"XML Content:\n{xml_content}")

        tree = ET.parse(config_file)
        root = tree.getroot()
        
        # Search for coupling-scheme tag
        coupling_scheme = root.find('.//coupling-scheme')
        
        if coupling_scheme is None:
            raise ValueError(f"No coupling scheme found in {config_file}")
        
        # Check type attribute
        type_attr = coupling_scheme.get('type')
        
        assert type_attr == expected_type, f"Expected {expected_type} coupling, got {type_attr}"
        print(f"✓ Verified {expected_type} coupling for {config_file}")

def test_strong_topology_implicit_coupling():
    test = TopologyCouplingTest()
    config_file = test._create_temp_config('strong')
    test._check_coupling_type(config_file, 'implicit')

def test_weak_topology_explicit_coupling():
    test = TopologyCouplingTest()
    config_file = test._create_temp_config('weak')
    test._check_coupling_type(config_file, 'explicit')

if __name__ == '__main__':
    pytest.main([__file__])