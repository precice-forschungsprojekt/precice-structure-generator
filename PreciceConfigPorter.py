import os
import re

def port_v2_to_v3(logger, input_file="./controller/examples/4/precice-config.xml", output_file="./_generated/config/precice-config-v3.xml"):
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        new_lines = []
        solver_interface_attributes = []
        for line in lines:
            # Remove solver-interface line and save attributes
            if "<solver-interface" in line:
                solver_interface_attributes = get_attributes(line)
                logger.info(f"Found solver-interface with attributes {solver_interface_attributes}")
                line = ""
            
            # Participants transformations
            if 'use-mesh' in line:
                if 'provide="yes"' in line:
                    line = (XMLTransformer(line, logger)
                            .rename_tag('use-mesh', 'provide-mesh')
                            .remove_attribute('provide')
                            .get_line())
                elif 'provide="no"' in line:
                    line = (XMLTransformer(line, logger)
                            .rename_tag('use-mesh', 'receive-mesh')
                            .remove_attribute('provide')
                            .get_line())
                else:
                    line = (XMLTransformer(line, logger)
                            .rename_tag('use-mesh', 'receive-mesh')
                            .get_line())
            
            # Example of complex transformation
            if 'read-data:' in line and 'waveform-order="1"' in line:
                line = (XMLTransformer(line, logger)
                        .rename_tag('read-data:', 'data:scalar/vector')
                        .replace_attribute('waveform-order', 'waveform-degree')
                        .get_line())
            
            # M2N attribute transformations
            if 'm2n:' in line:
                line = (XMLTransformer(line, logger)
                        .replace_attribute('from', 'acceptor')
                        .replace_attribute('to', 'connector')
                        .get_line())
            
            # Mapping constraint transformations
            if 'scaled-consistent' in line:
                line = line.replace('scaled-consistent', 'scaled-consistent-surface')
            
            new_lines.append(line)

        if not os.path.isfile(output_file):
            with open(output_file, 'w') as f:
                f.write("")
            logger.info(f"Creating output file at default path because it does not exist: {output_file}")
        
        with open(output_file, 'w') as f:
            f.writelines(new_lines)

        logger.info(f"Converted preCICE config from v2 to v3: {output_file}")

    except FileNotFoundError:
        logger.error(f"Input Precice v2 file {input_file} not found.")
    except Exception as e:
        logger.error(f"Error converting preCICE config: {str(e)}")

class XMLTransformer:
    def __init__(self, line: str, logger=None):
        """
        Initialize the XMLTransformer with a line and optional logger
        
        Args:
            line (str): Input XML line to transform
            logger (optional): Logger for tracking transformations
        """
        self.line = line
        self.logger = logger
    
    def rename_tag(self, input_tag: str, output_tag: str):
        """Rename an XML tag"""
        self.line = xml_transform(
            self.line, 
            input_tag=input_tag, 
            output_tag=output_tag, 
            logger=self.logger
        )
        return self
    
    def remove_attribute(self, attr: str):
        """Remove a specific attribute from an XML tag"""
        self.line = xml_transform(
            self.line, 
            remove_attrs=[attr], 
            logger=self.logger
        )
        return self
    
    def add_attribute(self, attr: str, value: str):
        """Add a new attribute to an XML tag"""
        self.line = xml_transform(
            self.line, 
            add_attrs={attr: value}, 
            logger=self.logger
        )
        return self
    
    def replace_attribute(self, old_attr: str, new_attr: str):
        """Replace an attribute name while preserving its value"""
        self.line = xml_transform(
            self.line, 
            replace_attrs={old_attr: new_attr}, 
            logger=self.logger
        )
        return self
    
    def transform(self, 
                  input_tag: str = None, 
                  output_tag: str = None, 
                  remove_attrs: list = None, 
                  add_attrs: dict = None, 
                  replace_attrs: dict = None):
        """Perform comprehensive XML line transformations"""
        self.line = xml_transform(
            self.line, 
            input_tag=input_tag, 
            output_tag=output_tag, 
            remove_attrs=remove_attrs, 
            add_attrs=add_attrs, 
            replace_attrs=replace_attrs, 
            logger=self.logger
        )
        return self
    
    def get_line(self):
        """Return the transformed line"""
        return self.line

def xml_transform(line: str, 
                 input_tag: str = None, 
                 output_tag: str = None, 
                 remove_attrs: list = None, 
                 add_attrs: dict = None, 
                 replace_attrs: dict = None, 
                 logger=None):
    """
    Perform comprehensive XML line transformations
    
    Args:
        line (str): Input XML line to transform
        input_tag (str, optional): Original tag name to replace
        output_tag (str, optional): New tag name
        remove_attrs (list, optional): List of attributes to remove
        add_attrs (dict, optional): Dictionary of attributes to add
        replace_attrs (dict, optional): Dictionary of attributes to replace
        logger (optional): Logger for tracking transformations
    
    Returns:
        str: Transformed XML line
    """
    # If line is empty or doesn't contain input tag, return original line
    if not line or (input_tag and input_tag not in line):
        return line
    
    # Extract indentation
    indentation = line.split('<')[0]
    
    # Parse current attributes
    attributes = get_attributes(line)
    
    # Rename tag if specified
    if input_tag and output_tag:
        line = line.replace(input_tag, output_tag)
    
    # Remove specified attributes
    if remove_attrs:
        for attr in remove_attrs:
            line = re.sub(f'{attr}="[^"]*"', '', line)
    
    # Replace attributes
    if replace_attrs:
        for old_attr, new_attr in replace_attrs.items():
            line = re.sub(f'{old_attr}="([^"]*)"', f'{new_attr}="\\1"', line)
    
    # Add new attributes
    if add_attrs:
        # Remove trailing />
        line = line.rstrip('/>') + ' '
        # Add new attributes
        for attr, value in add_attrs.items():
            line += f'{attr}="{value}" '
        # Close tag
        line = line.rstrip() + '/>'
    
    # Clean up whitespace
    line = re.sub(r'\s+>', '>', line)
    line = re.sub(r'\s{2,}', ' ', line)
    
    # Reattach indentation
    line = indentation + line.lstrip()
    
    if logger:
        logger.info(f"XML Transform: {line}")
    
    return line

def get_attributes(line):
    attributes = {}
    temp = line.split(' ')
    for attribute in temp:
        if '=' in attribute:
            key, value = create_key_value_pair(attribute)
            attributes[key] = value
    return attributes

def create_key_value_pair(attribute_str):
    key, value = attribute_str.strip().split('=')
    key = re.sub(r'[^a-zA-Z0-9]', '', key)
    value = re.sub(r'[^a-zA-Z0-9]', '', value)
    return key, value

def replace_mesh_usage_tags(input_string: str, attribute: str, new_attribute: str, line: str, logger):
    # Handle special case for 'No provide attribute exists'
    if attribute == 'No provide attribute exists':
        return XMLTransformer(line, logger).rename_tag(input_string, new_attribute).get_line()
    
    # For other cases, check if the specific attribute exists
    attributes = get_attributes(line)
    key, value = create_key_value_pair(attribute)
    
    if attributes.get(key) == value:
        return (XMLTransformer(line, logger)
                .rename_tag(input_string, new_attribute)
                .remove_attribute('provide')
                .get_line())
    
    return line