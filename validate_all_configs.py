#!/usr/bin/env python3

import os
from pathlib import Path
import sys
import glob
from validate_config import load_schema, convert_xml_to_json, validate_config

def find_precice_configs(start_path):
    """Find all preCICE configuration files recursively."""
    configs = []
    for root, _, files in os.walk(start_path):
        for file in files:
            if file.startswith('precice-config') and file.endswith('.xml'):
                configs.append(os.path.join(root, file))
    return configs

def main():
    # Get the path to the tutorials directory
    tutorials_dir = Path(__file__).parent / 'tutorials'
    schema_path = Path(__file__).parent / 'schemas' / 'precice-config-schema.json'

    # Load the schema once
    print(f"Loading schema from: {schema_path}")
    schema = load_schema(schema_path)

    # Find all config files
    print("\nSearching for preCICE configuration files...")
    config_files = find_precice_configs(tutorials_dir)
    
    if not config_files:
        print("No preCICE configuration files found!")
        return

    print(f"\nFound {len(config_files)} configuration files.")
    
    # Track validation results
    valid_configs = []
    invalid_configs = []

    # Validate each config
    for config_file in config_files:
        print(f"\n{'='*80}")
        print(f"Validating: {config_file}")
        try:
            json_data = convert_xml_to_json(config_file)
            if validate_config(json_data, schema):
                valid_configs.append(config_file)
            else:
                invalid_configs.append(config_file)
        except Exception as e:
            print(f"Error processing {config_file}: {e}")
            invalid_configs.append(config_file)

    # Print summary
    print(f"\n{'='*80}")
    print("\nValidation Summary:")
    print(f"Total configurations: {len(config_files)}")
    print(f"Valid configurations: {len(valid_configs)}")
    print(f"Invalid configurations: {len(invalid_configs)}")

    if invalid_configs:
        print("\nInvalid configurations:")
        for config in invalid_configs:
            print(f"  - {config}")

if __name__ == '__main__':
    main()
