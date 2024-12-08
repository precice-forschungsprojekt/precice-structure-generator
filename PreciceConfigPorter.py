import os
import re

def port_v2_to_v3(logger, input_file="./controller/examples/4/precice-config.xml", output_file="./_generated/config/precice-config-v3.xml"):
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        new_lines = []
        solver_interface_attributes = []
        for line in lines:
            new_line = line
            # Remove solver-interface line and save attributes
            if "<solver-interface" in line:
                solver_interface_attributes = get_attributes(line)
                logger.info(f"Found solver-interface with attributes {solver_interface_attributes}")
                new_line = ""
            
            # Participants
            new_line = replace_mesh_usage_tags('use-mesh', 'provide="yes"', 'provide-mesh', line, logger)
            new_line = replace_mesh_usage_tags('use-mesh', 'provide="no"', 'receive-mesh', line, logger)
            new_line = replace_mesh_usage_tags('use-mesh', 'No provide attribute exists', 'receive-mesh', line, logger)
            #new_line = port_v2_to_v3_replace_attribute('read-data:', 'waveform-order="1"', 'data:scalar/vector', line, logger)
            

            new_lines.append(new_line)
        
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

def port_v2_to_v3_replace(input_string: str, output_string: str, line: str, logger) -> str:
    if input_string in line:
        logger.info(f"Replaced {input_string} with {output_string}")
        logger.info(f"attributes {get_attributes(line)}")
        return line.replace(input_string, output_string)
    else:
        return line

def replace_mesh_usage_tags(input_string: str, attribute: str, new_attribute: str, line: str, logger):
    # If the input_string is not in the line, return the original line
    if input_string not in line:
        return line
    
    # Extract the indentation
    indentation = line.split('<')[0]
    
    # Parse the attributes
    attributes = get_attributes(line)
    #logger.info(f"Current attributes: {attributes}")
    
    # If attribute is a special flag indicating no specific attribute check
    if attribute == 'No provide attribute exists':
        # Simply replace the tag name
        new_line = line.replace(input_string, new_attribute)
        
        # Remove extra whitespace
        new_line = re.sub(r'\s+>', '>', new_line)
        new_line = re.sub(r'\s{2,}', ' ', new_line)
        
        # Reattach the original indentation
        new_line = indentation + new_line.lstrip()
        
        logger.info(f"Replaced '{input_string}' with '{new_attribute}' without attribute check")
        return new_line
    
    # Extract the key and value from the input attribute
    key, value = create_key_value_pair(attribute)
    #logger.info(f"Searching for attribute key: {key}, value: {value}")
    
    # Check if the attribute exists with the specified value
    if attributes.get(key) == value:
        # Remove the original attribute from the line
        for attr in list(attributes.keys()):
            if attr != 'name':  # Preserve the name attribute
                line = re.sub(f'{attr}="[^"]*"', '', line)
        
        # Replace the tag name and add back the indentation
        new_line = line.replace(input_string, new_attribute)
        
        # Remove extra whitespace
        new_line = re.sub(r'\s+>', '>', new_line)
        new_line = re.sub(r'\s{2,}', ' ', new_line)
        
        # Reattach the original indentation
        new_line = indentation + new_line.lstrip()
        
        logger.info(f"Replaced '{input_string}' with '{new_attribute}'")
        return new_line
    
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

def rename_tag(line: str, input_tag: str, output_tag: str, logger=None):
    """Rename an XML tag"""
    return xml_transform(line, input_tag=input_tag, output_tag=output_tag, logger=logger)

def remove_attribute(line: str, attr: str, logger=None):
    """Remove a specific attribute from an XML tag"""
    return xml_transform(line, remove_attrs=[attr], logger=logger)

def add_attribute(line: str, attr: str, value: str, logger=None):
    """Add a new attribute to an XML tag"""
    return xml_transform(line, add_attrs={attr: value}, logger=logger)

def replace_attribute(line: str, old_attr: str, new_attr: str, logger=None):
    """Replace an attribute name while preserving its value"""
    return xml_transform(line, replace_attrs={old_attr: new_attr}, logger=logger)

def rename_tag_and_remove_attribute(line: str, input_tag: str, output_tag: str, attr: str, logger=None):
    """Rename a tag and remove a specific attribute"""
    return xml_transform(line, 
                         input_tag=input_tag, 
                         output_tag=output_tag, 
                         remove_attrs=[attr], 
                         logger=logger)

def rename_tag_and_replace_attribute(line: str, input_tag: str, output_tag: str, old_attr: str, new_attr: str, logger=None):
    """Rename a tag and replace an attribute"""
    return xml_transform(line, 
                         input_tag=input_tag, 
                         output_tag=output_tag, 
                         replace_attrs={old_attr: new_attr}, 
                         logger=logger)