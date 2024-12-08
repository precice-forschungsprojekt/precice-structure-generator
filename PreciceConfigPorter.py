import os


def port_v2_to_v3(input_file, output_file="./_generated/config/precice-config-v3.xml", logger):
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            #The main preCICE header file and the main object was renamed. This means that you need to:
            if '#include "precice/SolverInterface.hpp"' in line:
                new_line = line.replace('','#include "precice/precice.hpp"')
            if 'precice::SolverInterface' in line:
                new_line = line.replace('precice::SolverInterface', 'precice::Participant')



            new_lines.append(new_line)
        if not(os.path.isfile(output_file)):
            with open(output_file,'w') as f:
                f.write("")
            logger.info(f"Creating output file at default path because it does not exist: ./_generated/config/precice-config-v3.xml")
        with open(input_file, 'w') as f:
            f.writelines(new_lines)

    except FileNotFoundError:
        logger.error(f"Input Precice v2 file {input_file} not found.")