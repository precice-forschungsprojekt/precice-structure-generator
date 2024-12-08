import xml.etree.ElementTree as ET
import re

class PreciceConfigPorter:
    def __init__(self, config_path):
        """
        Initialize the config porter with the path to the preCICE configuration file.
        
        :param config_path: Path to the preCICE XML configuration file
        """
        self.config_path = config_path
        self.tree = ET.parse(config_path)
        self.root = self.tree.getroot()

    def port_solver_interface(self):
        """
        Port the <solver-interface> tag to the new configuration structure.
        Removes <solver-interface> tag and moves attributes to <precice-configuration>.
        """
        # Remove solver-interface tag and move its attributes
        solver_interface = self.root.find('.//solver-interface')
        if solver_interface is not None:
            # Move sync-mode to profiling tag
            sync_mode = solver_interface.get('sync-mode')
            profiling = self.root.find('.//profiling')
            if profiling is not None and sync_mode:
                profiling.set('sync-mode', sync_mode)
            
            # Remove solver-interface tag
            self.root.remove(solver_interface)

    def port_dimensions(self):
        """
        Move dimensions configuration from solver-interface to individual mesh tags.
        """
        # Find all mesh tags and set dimensions if not already set
        meshes = self.root.findall('.//mesh')
        for mesh in meshes:
            if 'dimensions' not in mesh.attrib:
                # Default to 3 if not specified
                mesh.set('dimensions', '3')

    def port_m2n_attributes(self):
        """
        Rename m2n attributes from 'from/to' to 'acceptor/connector'.
        """
        m2n_tags = self.root.findall('.//m2n')
        for m2n in m2n_tags:
            if 'from' in m2n.attrib:
                m2n.set('acceptor', m2n.get('from'))
                m2n.attrib.pop('from')
            
            if 'to' in m2n.attrib:
                m2n.set('connector', m2n.get('to'))
                m2n.attrib.pop('to')

    def port_rbf_mapping(self):
        """
        Update RBF mapping configuration to new format.
        """
        rbf_mappings = self.root.findall('.//mapping:rbf')
        for rbf in rbf_mappings:
            # Update any deprecated RBF attributes or configurations
            # This is a placeholder for specific RBF mapping changes
            pass

    def port_header(self):
        """
        Update the configuration header and root tag.
        """
        # Replace solver-interface with precice-configuration if not already done
        if self.root.tag == 'solver-interface':
            self.root.tag = 'precice-configuration'

    def save_config(self, output_path=None):
        """
        Save the ported configuration to a new file.
        
        :param output_path: Path to save the new configuration. 
                             If None, overwrites the original file.
        """
        if output_path is None:
            output_path = self.config_path
        
        self.tree.write(output_path, encoding='utf-8', xml_declaration=True)

    def port_config(self):
        """
        Perform all porting operations in sequence.
        """
        self.port_header()
        self.port_solver_interface()
        self.port_dimensions()
        self.port_m2n_attributes()
        self.port_rbf_mapping()
        
        return self

def port_precice_config(input_config_path, output_config_path=None):
    """
    Convenience function to port a preCICE configuration file.
    
    :param input_config_path: Path to the input v2.x configuration file
    :param output_config_path: Path to save the ported v3.x configuration. 
                                If None, overwrites the input file.
    :return: Ported configuration file path
    """
    porter = PreciceConfigPorter(input_config_path)
    porter.port_config()
    porter.save_config(output_config_path)
    return output_config_path or input_config_path

# Example usage
if __name__ == '__main__':
    # Example of how to use the config porter
    port_precice_config('precice_config_v2.xml', 'precice_config_v3.xml')
