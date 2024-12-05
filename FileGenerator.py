from pathlib import Path
from generation_utils.StructureHandler import StructureHandler
import yaml
from generation_utils.Logger import Logger
from controller_utils.ui_struct.UI_UserInput import UI_UserInput
from controller_utils.myutils.UT_PCErrorLogging import UT_PCErrorLogging
from controller_utils.precice_struct import PS_PreCICEConfig
import argparse

class FileGenerator:
    def __init__(self, file: Path) -> None:
        """ Class which takes care of generating the content of the necessary files
            :param file: Input yaml file that is needed for generation of the precice-config.xml file"""
        self.input_file = file
        self.precice_config = PS_PreCICEConfig()
        self.mylog = UT_PCErrorLogging()
        self.user_ui = UI_UserInput()
        self.logger = Logger()
        self.structure = StructureHandler()

    def generate_precice_config(self) -> None:
        """Generates the precice-config.xml file based on the topology.yaml file."""

        # Try to open the yaml file and get the configuration
        try:
            with open(self.input_file, "r") as config_file:
                config = yaml.load(config_file.read(), Loader=yaml.SafeLoader)
                self.logger.info(f"Input YAML file: {self.input_file}")
        except FileNotFoundError:
            self.logger.error(f"Input YAML file {self.input_file} not found.")
            return
        except Exception as e:
            self.logger.error(f"Error reading input YAML file: {str(e)}")
            return

        # Build the ui
        self.logger.info("Building the user input info...")
        self.user_ui.init_from_yaml(config, self.mylog)

        # Generate the precice-config.xml file
        self.logger.info("Generating preCICE config...")
        self.precice_config.create_config(self.user_ui)

        # Set the target of the file and write out to it
        # Warning: self.structure.precice_config is of type Path, so it needs to be converted to str
        target = str(self.structure.precice_config)
        try:
            self.logger.info(f"Writing preCICE config to {target}...")
            self.precice_config.write_precice_xml_config(target, self.mylog)
        except Exception as e:
            self.logger.error(f"Failed to write preCICE XML config: {str(e)}")
            return

        self.logger.success(f"XML generation completed successfully: {target}")

    def generate_README(self) -> None:
        """Generates the README.md file"""
        try:
            origin_template_README = Path(__file__).parent / "templates" / "template_README.md"
            self.logger.info("Reading in the template file for README.md")

            # Check if the template file exists
            if not origin_template_README.exists():
                raise FileNotFoundError(f"Template file not found: {origin_template_README}")

            # Read the template content
            template_content = origin_template_README.read_text(encoding="utf-8")

            # Set the target for the README.md
            target = self.structure.README

            self.logger.info(f"Writing the template to the target: {str(target)}")

            # Write content to the target file
            with open(target, 'w', encoding="utf-8") as README:
                README.write(template_content)

            self.logger.success(f"Successfully written README.md content to: {str(target)}")

        except FileNotFoundError as fileNotFoundException:
            self.logger.error(f"File not found: {fileNotFoundException}")
        except PermissionError as premissionErrorException:
            self.logger.error(f"Permission error: {premissionErrorException}")
        except Exception as generalExcpetion:
            self.logger.error(f"An unexpected error occurred: {generalExcpetion}")

    def generate_run(self) -> None:
        """Generates the run.sh file"""
        #TODO
        pass

    def generate_clean(self) -> None:
        """Generates the clean.sh file."""
        #TODO
        pass

    def generate_adapter_config(self) -> None:
        """Generates the adapter-config.json file."""
        #TODO
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Takes topology.yaml files as input and writes out needed files to start the precice.")
    parser.add_argument(
        "-f", "--file", 
        type=Path, 
        required=False, 
        help="Input topology.yaml file",
        default=Path("controller/examples/1/topology.yaml")
    )
    args = parser.parse_args()

    fileGenerator = FileGenerator(args.file)
    fileGenerator.generate_precice_config()
    fileGenerator.generate_README()
