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
            new_line = port_v2_to_v3_replace_attribute('use-mesh', 'provide="yes"', 'provide-mesh', line, logger)
            new_line = port_v2_to_v3_replace_attribute('use-mesh', 'provide="no"', 'receive-mesh', new_line, logger)

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

def port_v2_to_v3_replace_attribute(input_string: str, attribute: str, new_attribute: str, line: str, logger):
    # If the input_string is not in the line, return the original line
    if input_string not in line:
        return line
    
    # Extract the indentation
    indentation = line.split('<')[0]
    
    # Parse the attributes
    attributes = get_attributes(line)
    logger.info(f"Current attributes: {attributes}")
    
    # Extract the key and value from the input attribute
    key, value = create_key_value_pair(attribute)
    logger.info(f"Searching for attribute key: {key}, value: {value}")
    
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
