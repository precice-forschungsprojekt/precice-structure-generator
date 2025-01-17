from pathlib import Path
import yaml
from generation_utils.AdapterConfigGenerator import AdapterConfigGenerator

class FileGeneratorMethods:
    def __init__(self, input_file, structure, precice_config, user_ui, logger, mylog):
        """Initialize the FileGeneratorMethods with necessary dependencies."""
        self.input_file = input_file
        self.structure = structure
        self.precice_config = precice_config
        self.user_ui = user_ui
        self.logger = logger
        self.mylog = mylog

    def _generate_precice_config(self) -> None:
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
            self.precice_config.write_precice_xml_config(
            target, self.mylog, sync_mode=self.user_ui.sim_info.sync_mode, mode=self.user_ui.sim_info.mode
        )

        except Exception as e:
            self.logger.error(f"Failed to write preCICE XML config: {str(e)}")
            return

        self.logger.success(f"XML generation completed successfully: {target}")
    
    def _generate_static_files(self, target: Path, name: str) -> None:
        """Generate static files from templates"""
        # [Your existing _generate_static_files method]

    def _generate_README(self) -> None:
        """Generates the README.md file"""
        self._generate_static_files(target=self.structure.README,
                                    name="README.md")

    def _generate_run(self) -> None:
        """Generates the run.sh file"""
        self._generate_static_files(target=self.structure.run,
                                    name="run.sh")

    def _generate_clean(self) -> None:
        """Generates the clean.sh file."""
        self._generate_static_files(target=self.structure.clean,
                                    name="clean.sh")

    def _generate_adapter_config(self, target_participant: str, adapter_config: Path) -> None:
        """Generates the adapter-config.json file."""
        adapter_config_generator = AdapterConfigGenerator(adapter_config_path=adapter_config,
                                                          precice_config_path=self.structure.precice_config, 
                                                          target_participant=target_participant)
        adapter_config_generator.write_to_file()
    
    def generate_level_0(self) -> None:
        """Fills out the files of level 0 (everything in the root folder)."""
        self._generate_clean()
        self._generate_README()
        self._generate_precice_config()
    
    def _extract_participants(self) -> list[str]:
        """Extracts the participants from the topology.yaml file."""
        try:
            with open(self.input_file, "r") as config_file:
                config = yaml.load(config_file.read(), Loader=yaml.SafeLoader)
                self.logger.info(f"Input YAML file: {self.input_file}")
        except FileNotFoundError:
            self.logger.error(f"Input YAML file {self.input_file} not found.")
            return []
        except Exception as e:
            self.logger.error(f"Error reading input YAML file: {str(e)}")
            return []
        
        return list(config["participants"].keys())
    
    def generate_level_1(self) -> None:
        """Generates the files of level 1 (everything in the generated sub-folders)."""
        participants = self._extract_participants()
        for participant in participants:
            target_participant = self.structure.create_level_1_structure(participant)
            adapter_config = target_participant[1]
            run_sh = target_participant[2]
            self._generate_adapter_config(target_participant=participant, adapter_config=adapter_config)
            self._generate_run()