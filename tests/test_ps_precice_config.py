import os
import shutil
import xml.etree.ElementTree as ET
from FileGenerator import FileGenerator

class TopologyCouplingTest:
    def __init__(self):
        self.template_config = r'controller_utils/examples/1/precice-config.xml'
        self.output_dir = r'tests/generation-tests/topology_coupling_tests'
        os.makedirs(self.output_dir, exist_ok=True)

    def _create_temp_config(self, topology_type):
        # Create a unique filename for each topology type
        output_filename = os.path.join(self.output_dir, f'precice_config_{topology_type}.xml')
        
        # Copy the template config
        shutil.copy(self.template_config, output_filename)
        
        # Generate config using FileGenerator with specified topology type
        file_generator = FileGenerator()
        file_generator.generate_precice_config(
            input_file=output_filename, 
            output_file=output_filename, 
            topology_type=topology_type
        )
        
        return output_filename

    def _check_coupling_type(self, config_file, expected_type):
        tree = ET.parse(config_file)
        root = tree.getroot()
        
        # Search for coupling-scheme tag
        coupling_scheme = root.find('.//coupling-scheme:coupling-scheme', 
                                    namespaces={'coupling-scheme': 'coupling-scheme'})
        
        if coupling_scheme is None:
            raise ValueError(f"No coupling scheme found in {config_file}")
        
        # Check type attribute
        type_attr = coupling_scheme.get('type')
        
        if expected_type == 'implicit' and type_attr != 'implicit':
            raise AssertionError(f"Expected implicit coupling, got {type_attr}")
        elif expected_type == 'explicit' and type_attr != 'explicit':
            raise AssertionError(f"Expected explicit coupling, got {type_attr}")
        
        print(f"✓ Verified {expected_type} coupling for {config_file}")

    def run_tests(self):
        # Test scenarios
        topology_types = [
            {'type': 'strong', 'expected_coupling': 'implicit'},
            {'type': 'weak', 'expected_coupling': 'explicit'}
        ]

        for scenario in topology_types:
            config_file = self._create_temp_config(scenario['type'])
            self._check_coupling_type(config_file, scenario['expected_coupling'])

def main():
    test = TopologyCouplingTest()
    test.run_tests()
    print("All topology coupling tests passed successfully!")

if __name__ == '__main__':
    main()