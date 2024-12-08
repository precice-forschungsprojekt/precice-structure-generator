import os

def port_v2_to_v3(logger, input_file, output_file="./_generated/config/precice-config-v3.xml"):
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            #The main preCICE header file and the main object was renamed. This means that you need to:
            new_line = line  # Default to original line if no replacement needed
            if '#include "precice/SolverInterface.hpp"' in line:
                new_line = line.replace('#include "precice/SolverInterface.hpp"', '#include "precice/precice.hpp"')
            #if 'solver-interface' in line:
            #    new_line = line.replace('solver-interface', 'participant')
            new_line = port_v2_to_v3_replace('solver-interface', 'participant', line)
            #TOD ?? Consider renaming your objects from, e.g., interface to participant, to better reflect the purpose and to be consistent with the rest of the changes
            #Steering methods
            

            #####
            new_lines.append(new_line)
        if not(os.path.isfile(output_file)):
            with open(output_file,'w') as f:
                f.write("")
            logger.info(f"Creating output file at default path because it does not exist: ./_generated/config/precice-config-v3.xml")
        with open(output_file, 'w') as f:
            f.writelines(new_lines)

        """ Alternative implementation
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write to output file instead of modifying input file
        with open(output_file, 'w') as f:
            f.writelines(new_lines)
        
        logger.info(f"Converted preCICE config from v2 to v3: {output_file}")
        """


        logger.info(f"Converted preCICE config from v2 to v3: {output_file}")

    except FileNotFoundError:
        logger.error(f"Input Precice v2 file {input_file} not found.")
    except Exception as e:
        logger.error(f"Error converting preCICE config: {str(e)}")



def port_v2_to_v3_replace(input_string:str,output_string:str,line):
    if input_string in line:
        return line.replace(input_string, output_string)
    else:
        return line