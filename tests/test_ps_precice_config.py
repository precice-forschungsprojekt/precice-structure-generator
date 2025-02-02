import os
import shutil
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
        # Read the XML content
        with open(config_file, 'r') as f:
            xml_content = f.read()
            print(f"XML Content:\n{xml_content}")

        # Find the coupling scheme line
        coupling_scheme_line = [line for line in xml_content.split('\n') if 'coupling-scheme:' in line][0].strip()
        
        # Determine coupling type based on the line
        if expected_type == 'implicit':
            assert 'parallel-implicit' in coupling_scheme_line or 'implicit' in coupling_scheme_line, \
                f"Expected implicit coupling, got line: {coupling_scheme_line}"
        else:  # explicit
            assert 'parallel-explicit' in coupling_scheme_line or 'explicit' in coupling_scheme_line, \
                f"Expected explicit coupling, got line: {coupling_scheme_line}"
        
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