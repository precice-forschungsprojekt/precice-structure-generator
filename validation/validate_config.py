#!/usr/bin/env python3

import json
import xmltodict
import jsonschema
import argparse
import sys
from pathlib import Path

def convert_xml_to_json(xml_path):
    """Convert XML file to JSON format."""
    with open(xml_path, 'r') as f:
        xml_content = f.read()
    
    # Parse XML to dict with attribute preservation and force lists
    json_dict = xmltodict.parse(xml_content, attr_prefix='@', force_list={
        'data:vector',
        'use-data',
        'provide-mesh',
        'receive-mesh',
        'read-data',
        'write-data',
        'mapping:rbf',
        'watch-point',
        'exchange'
    })
    return json_dict

def load_schema(schema_path):
    """Load JSON schema from file."""
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading schema file: {e}")
        sys.exit(1)

def validate_config(json_data, schema):
    """Validate JSON data against schema."""
    try:
        jsonschema.validate(instance=json_data, schema=schema)
        print("Configuration is valid! ")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"Validation error: {e.message}")
        print(f"Failed at path: {' -> '.join(str(x) for x in e.path)}")
        return False
    except jsonschema.exceptions.SchemaError as e:
        print(f"Schema error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Validate preCICE XML configuration against schema')
    parser.add_argument('config_file', type=str, help='Path to preCICE XML configuration file')
    parser.add_argument('--schema', type=str, 
                      default=str(Path(__file__).parent / 'schemas' / 'precice-config-schema.json'),
                      help='Path to JSON schema file (default: schemas/precice-config-schema.json)')
    parser.add_argument('--save-json', type=str, help='Save converted JSON to file')
    
    args = parser.parse_args()

    # Load and validate files exist
    if not Path(args.config_file).exists():
        print(f"Error: Config file not found: {args.config_file}")
        sys.exit(1)
    if not Path(args.schema).exists():
        print(f"Error: Schema file not found: {args.schema}")
        sys.exit(1)

    # Convert XML to JSON
    print(f"Converting XML configuration: {args.config_file}")
    json_data = convert_xml_to_json(args.config_file)

    # Save JSON if requested
    if args.save_json:
        try:
            with open(args.save_json, 'w') as f:
                json.dump(json_data, f, indent=2)
            print(f"Saved JSON to: {args.save_json}")
        except Exception as e:
            print(f"Error saving JSON file: {e}")

    # Load schema
    print(f"Loading schema: {args.schema}")
    schema = load_schema(args.schema)

    # Validate
    print("\nValidating configuration...")
    is_valid = validate_config(json_data, schema)
    
    sys.exit(0 if is_valid else 1)

if __name__ == '__main__':
    main()
