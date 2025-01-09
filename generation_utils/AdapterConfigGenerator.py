from pathlib import Path
from generation_utils.Logger import Logger
from lxml import etree
import json
import re

class AdapterConfigGenerator:
    def __init__(self, adapter_config_path: Path, precice_config_path: Path, target_participant: str) -> None:
        """
        Initializes the AdapterConfigGenerator with paths to the adapter config and precice config.

        Args:
            adapter_config_path (Path): Path to the output adapter-config.json file.
            precice_config_path (Path): Path to the input precice-config.xml file.
            target_participant (str): Name of the participant to generate config for.
        """
        self.adapter_config_path = adapter_config_path
        self.logger = Logger()
        self.precice_config_path = precice_config_path
        self.target_participant = target_participant

        # Initialize the config dictionary that matches the schema
        self.adapter_config = {
            "participant_name": target_participant,
            "config_file_name": "../precice-config.xml",
            "interfaces": []
        }

    def _get_generated_precice_config(self):
        """
        Parses the precice-config.xml file, removes namespaces, and stores the root element.
        """
        try:
            with open(self.precice_config_path, 'r', encoding='utf-8') as precice_config_file:
                precice_config = precice_config_file.read()
        except FileNotFoundError:
            self.logger.error(f"PreCICE config file not found at {self.precice_config_path}")
            raise

        # Parse with lxml and clean namespaces
        parser = etree.XMLParser(ns_clean=True, recover=True)
        try:
            doc = etree.fromstring(precice_config.encode('utf-8'), parser=parser)
        except etree.XMLSyntaxError as e:
            self.logger.error(f"Error parsing XML: {e}")
            raise

        # Strip namespace prefixes from tags
        for elem in doc.iter():
            if isinstance(elem.tag, str) and '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        self.root = doc
        self.logger.info("Parsed precice-config.xml successfully.")

    def _validate_name(self, name: str, pattern: str, description: str) -> bool:
        """
        Validate a name against a given regex pattern.

        Args:
            name (str): Name to validate
            pattern (str): Regex pattern to match
            description (str): Description of the name for error logging

        Returns:
            bool: True if name is valid, False otherwise
        """
        if not re.match(pattern, name):
            self.logger.error(f"Invalid {description}: {name}")
            return False
        return True

    def _fill_out_adapter_config(self):
        """
        Fills out the adapter configuration based on the precice-config.xml data.
        """
        self._get_generated_precice_config()

        # Debug: Print all XML content
        xml_content = etree.tostring(self.root, pretty_print=True).decode()

        # Find the target participant (case-insensitive and partial match)
        participant_elem = None
        all_participants = self.root.findall(".//participant")
        self.logger.info(f"Total participants found: {len(all_participants)}")
        
        for participant in all_participants:
            participant_name = participant.get("name", "").lower()
            target_name = self.target_participant.lower()
            
            self.logger.info(f"Checking participant: {participant_name}")
            
            if participant_name == target_name or target_name in participant_name:
                participant_elem = participant
                break

        if participant_elem is None:
            self.logger.error(f"Participant '{self.target_participant}' not found in precice-config.xml.")
            # Log all participant names for debugging
            all_participant_names = [p.get("name", "N/A") for p in all_participants]
            self.logger.info(f"Available participants: {all_participant_names}")
            return

        # Validate participant name
        if not self._validate_name(
            self.target_participant, 
            r'^[A-Z][a-zA-Z0-9-]*$', 
            "participant name"
        ):
            return

        # Find all meshes and data in the XML
        all_meshes = self.root.findall(".//mesh")
        all_write_data = self.root.findall(".//write-data")
        all_read_data = self.root.findall(".//read-data")

        # Filter meshes and data for this participant
        participant_name = participant_elem.get("name")
        meshes = []
        write_data_list = []
        read_data_list = []

        # Find meshes and data related to this participant
        for mesh in all_meshes:
            # Check if mesh is related to this participant through provide-mesh or receive-mesh
            provide_mesh_elems = participant_elem.findall(f".//provide-mesh[@name='{mesh.get('name')}']")
            receive_mesh_elems = participant_elem.findall(f".//receive-mesh[@name='{mesh.get('name')}']")
            
            if provide_mesh_elems or receive_mesh_elems:
                meshes.append(mesh)

        # Find write and read data for these meshes
        for mesh in meshes:
            mesh_name = mesh.get("name")
            
            # Find write data for this mesh
            for write_data in all_write_data:
                if write_data.get("mesh_name") == mesh_name:
                    write_data_list.append(write_data)

            # Find read data for this mesh
            for read_data in all_read_data:
                if read_data.get("mesh_name") == mesh_name:
                    read_data_list.append(read_data)

        # Debug logging
        self.logger.info(f"Found meshes: {[mesh.get('name') for mesh in meshes]}")
        self.logger.info(f"Found write data: {[data.get('name') for data in write_data_list]}")
        self.logger.info(f"Found read data: {[data.get('name') for data in read_data_list]}")

        # Create interfaces based on meshes
        for mesh in meshes:
            mesh_name = mesh.get("name")
            
            # More lenient mesh name validation - remove the strict validation
            interface = {
                "mesh_name": mesh_name,
                "patches": [], 
                "write_data_names": [],
                "read_data_names": []
            }

            # Add write data names
            for write_data in write_data_list:
                if write_data.get("mesh_name") == mesh_name:
                    data_name = write_data.get("name")
                    if data_name:
                        interface["write_data_names"].append(data_name)

            # Add read data names
            for read_data in read_data_list:
                if read_data.get("mesh_name") == mesh_name:
                    data_name = read_data.get("name")
                    if data_name:
                        interface["read_data_names"].append(data_name)

            # Only add interface if it has data names
            if interface["write_data_names"] or interface["read_data_names"]:
                self.adapter_config["interfaces"].append(interface)
            else:
                self.logger.info(f"No data names found for mesh: {mesh_name}")

        # Validate that at least one interface was created
        if not self.adapter_config["interfaces"]:
            self.logger.error(f"No valid interfaces found for participant '{self.target_participant}'")      


    def write_to_file(self) -> None:
        """
        Writes the filled adapter configuration to the specified JSON file.
        """
        self._fill_out_adapter_config()

        try:
            with open(self.adapter_config_path, 'w', encoding='utf-8') as adapter_config_file:
                json.dump(self.adapter_config, adapter_config_file, indent=4)
            self.logger.success(f"Adapter configuration written to {self.adapter_config_path}")
        except IOError as e:
            self.logger.error(f"Failed to write adapter configuration to file: {e}")
            raise