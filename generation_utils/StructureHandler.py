from pathlib import Path
from .Logger import Logger
import shutil

class StructureHandler:
    def __init__(self, output_path: Path, clean_generated: bool = True) -> None:
        """ Creates the files and folders in a structure.
            :param clean_generated: If set to True, clean the _generated dir before the files are created.
            Can be useful if you added or adjusted files yourself and you are not sure what you changed."""
        # Objects
        self.root = output_path
        self.generated_root = self.root / "_generated"
        self.config_dir = self.generated_root / "config"
        self.logger = Logger()

        # Methods in pre-processing
        if clean_generated:
            self._cleaner()
        self._create_folder_sturcture()
        self._create_files()

    def _create_folder_sturcture(self) -> None:
        """Creates the structure needed for generated files"""
        try: 
            self.generated_root.mkdir(parents=True, exist_ok=True)
            self.logger.success(f"Created folder: {self.generated_root}")

            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.logger.success(f"Created folder: {self.config_dir}")
        except Exception as create_folder_structure_excpetion:
            self.logger.error(f"Failed to create folder structure. Error: {create_folder_structure_excpetion}")

    def _create_files(self) -> None:
        """Creates the necessary files."""

        # Files that need to be created
        files = [
            self.generated_root / "clean.sh",
            self.generated_root / "run.sh",
            self.generated_root / "README.md",
            self.config_dir / "precice-config.xml",
            self.config_dir / "adapter-config.json"
        ]

        self.clean, self.run, self.README, self.precice_config, self.adapter_config = files

        for file in files:
            try:
                file.touch(exist_ok=True)
                self.logger.success(f"Created file: {file}")
            except Exception as create_files_exception:
                self.logger.error(f"Failed to create file {file}. Error: {create_files_exception}")


    def _cleaner(self) -> None:
        """
        Removes the entire `self.generated_root` directory and its contents.
        If `self.generated_root` exists, it deletes everything inside it.
        """
        if self.generated_root.exists():
            try:
                # Remove the directory and all its contents
                shutil.rmtree(self.generated_root)
                self.logger.success(f"Successfully removed directory and all contents: {self.generated_root}")
            except Exception as cleaner_exception:
                self.logger.error(f"Failed to remove directory: {self.generated_root}. Error: {cleaner_exception}")
        else:
            self.logger.info(f"Directory {self.generated_root} does not exist. Nothing to clean.")