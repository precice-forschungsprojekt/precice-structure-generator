from pathlib import Path
from generation_utils.StructureHandler import StructureHandler
import yaml
from generation_utils.Logger import Logger
from controller_utils.ui_struct.UI_UserInput import UI_UserInput
from controller_utils.myutils.UT_PCErrorLogging import UT_PCErrorLogging
from controller_utils.precice_struct import PS_PreCICEConfig
import argparse
from generation_utils.FileGeneratorMethods import FileGeneratorMethods


class FileGenerator:
    def __init__(self, input_file: Path, output_path: Path) -> None:
        """ Class which takes care of generating the content of the necessary files
            :param input_file: Input yaml file that is needed for generation of the precice-config.xml file
            :param output_path: Path to the folder where the _generated/ folder will be placed"""
        self.input_file = input_file
        self.precice_config = PS_PreCICEConfig()
        self.mylog = UT_PCErrorLogging()
        self.user_ui = UI_UserInput()
        self.logger = Logger()
        self.structure = StructureHandler(output_path)
        self.methods = FileGeneratorMethods(
            input_file=self.input_file,
            structure=self.structure,
            precice_config=self.precice_config,
            user_ui=self.user_ui,
            logger=self.logger,
            mylog=self.mylog
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Takes topology.yaml files as input and writes out needed files to start the precice.")
    parser.add_argument(
        "-f", "--input-file", 
        type=Path, 
        required=False, 
        help="Input topology.yaml file",
        default=Path("controller_utils/examples/1_old/topology.yaml")
    )
    parser.add_argument(
        "-o", "--output-path",
        type=Path,
        required=False,
        help="Output path for the generated folder.",
        default=Path(__file__).parent
    )

    args = parser.parse_args()

    fileGenerator = FileGenerator(args.input_file, args.output_path)
    fileGenerator.methods.generate_level_0()
    fileGenerator.methods.generate_level_1()