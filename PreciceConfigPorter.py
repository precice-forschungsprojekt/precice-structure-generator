import os

def port_v2_to_v3(logger, input_file, output_file="./_generated/config/precice-config-v3.xml"):
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:

            new_line = port_v2_to_v3_replace('solver-interface', 'participant', line, logger)
            

            #####
            new_lines.append(new_line)
        if not(os.path.isfile(output_file)):
            with open(output_file,'w') as f:
                f.write("")
            logger.info(f"Creating output file at default path because it does not exist: ./_generated/config/precice-config-v3.xml")
        with open(output_file, 'w') as f:
            f.writelines(new_lines)

        logger.info(f"Converted preCICE config from v2 to v3: {output_file}")

    except FileNotFoundError:
        logger.error(f"Input Precice v2 file {input_file} not found.")
    except Exception as e:
        logger.error(f"Error converting preCICE config: {str(e)}")



def port_v2_to_v3_replace(input_string:str,output_string:str,line,logger):
    if input_string in line:
        logger.info(f"Replaced {input_string} with {output_string}")
        logger.info(f"attributes {get_attributes(line)}")
        return line.replace(input_string, output_string)
    else:
        return line
#def get_attributes(line):
    #attributes = {}
    #for attribute in line.split(' '):
    #    key, value = attribute.strip().split('=')
    #    attributes[key.strip()] = value.strip()
    #return attributes
    #return line.split(' ')

def parse_attributes(line):
    attributes = {}
    for attribute in line:
        if '=' in attribute:
            key, value = attribute.strip().split('=')
            key = key.strip()
            value = value.strip().strip('">')
            attributes[key] = value
    return attributes

# Example input
input_line = ['', '', '', '<solver-interface', 'dimensions="3">\n']

# Parse attributes
parsed_attributes = parse_attributes(input_line)
print(parsed_attributes)


