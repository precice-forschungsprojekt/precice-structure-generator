import sys
import os
from pathlib import Path
import pytest
import yaml
import json
import jsonschema
import difflib
import xml.etree.ElementTree as ET
import time
import traceback

def _get_examples():
    """Get the list of examples as ints in the examples directory"""
    root = Path(__file__).parent.parent.parent
    examples_dir = root / "controller_utils" / "examples"
    
    # Print all directories in the examples directory for debugging
    print("All directories in examples:")
    for item in examples_dir.iterdir():
        if item.is_dir():
            print(f" - {item.name}")
    
    # Filter and sort examples
    examples = sorted([example.name for example in examples_dir.iterdir() if example.is_dir()])
    
    print(f"Filtered examples: {examples}")
    
    # Limit to first 2 examples for testing
    return examples[:2]

def parse_xml_structure(file_path):
    """
    Custom XML parsing function specifically designed for precice config files.
    
    Args:
        file_path (Path): Path to the XML file
    
    Returns:
        dict: Nested dictionary representing XML structure
    """
    def debug_print_file_contents(file_path):
        """Print file contents for debugging."""
        print(f"\n--- File Contents: {file_path} ---")
        try:
            with open(file_path, 'r') as f:
                print(f.read())
        except Exception as e:
            print(f"Error reading file: {e}")
        print("--- End File Contents ---\n")

    def clean_attribute_value(value):
        """
        Clean and normalize attribute values.
        
        Removes:
        - Surrounding quotes
        - Extra whitespace
        - Trailing slashes or other unwanted characters
        """
        # Remove surrounding quotes and extra whitespace
        value = value.strip('\'"')
        
        # Remove any trailing non-alphanumeric characters
        import re
        value = re.sub(r'[^a-zA-Z0-9]+$', '', value)
        
        # Remove any extra whitespace
        value = value.strip()
        
        return value

    def parse_precice_config(lines):
        """
        Parse precice configuration with special handling for specific tags.
        
        Args:
            lines (list): Lines of the XML file
        
        Returns:
            dict: Parsed configuration structure
        """
        # Debug: print raw lines
        print(f"Parsing {len(lines)} lines")
        
        # Remove XML declaration and comments
        lines = [line.strip() for line in lines 
                 if line.strip() and 
                 not line.strip().startswith('<?') and 
                 not line.strip().startswith('<!--')]
        
        # Debug: print processed lines
        print(f"Processed lines: {len(lines)}")
        if not lines:
            debug_print_file_contents(file_path)
            raise ValueError(f"No valid lines found in {file_path}")
        
        def parse_element(start_index=0):
            """
            Recursively parse XML elements with precice-specific logic.
            
            Args:
                start_index (int): Starting line index
            
            Returns:
                tuple: (parsed element dict, next line index)
            """
            if start_index >= len(lines):
                print(f"Reached end of lines at index {start_index}")
                return None, start_index
            
            line = lines[start_index]
            print(f"Processing line: {line}")
            
            # Check for opening tag
            if not (line.startswith('<') and not line.startswith('</') and not line.startswith('<?')):
                print(f"Skipping line: {line}")
                return None, start_index + 1
            
            # Extract tag and attributes
            tag_parts = line[1:].split('>', 1)[0].split()
            tag_name = tag_parts[0].rstrip('/')
            
            # Parse attributes
            attributes = {}
            for attr in tag_parts[1:]:
                if '=' in attr:
                    key, value = attr.split('=', 1)
                    attributes[key] = clean_attribute_value(value)
            
            # Check for self-closing tag
            if line.endswith('/>'):
                return {
                    'tag': tag_name,
                    'attributes': attributes,
                    'children': [],
                    'text': ''
                }, start_index + 1
            
            # Initialize element
            element = {
                'tag': tag_name,
                'attributes': attributes,
                'children': [],
                'text': ''
            }
            
            # Parse children and text
            current_index = start_index + 1
            while current_index < len(lines):
                current_line = lines[current_index]
                
                # Check for closing tag
                if current_line.startswith(f'</{tag_name}>'):
                    return element, current_index + 1
                
                # Check for nested element
                if current_line.startswith('<') and not current_line.startswith('<!--'):
                    child, current_index = parse_element(current_index)
                    if child:
                        element['children'].append(child)
                    continue
                
                # Accumulate text content (if not just whitespace)
                if current_line and not current_line.startswith('<!--'):
                    element['text'] += current_line + ' '
                
                current_index += 1
            
            return element, current_index

        # Read and parse the entire configuration
        try:
            # Parse root element
            root, _ = parse_element()
            
            # Validate root
            if root is None:
                debug_print_file_contents(file_path)
                raise ValueError(f"Failed to parse XML structure in {file_path}")
            
            return root
        except Exception as e:
            print(f"Error parsing XML: {e}")
            debug_print_file_contents(file_path)
            raise

    # Wrapper to add more error handling
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        return parse_precice_config(lines)
    except Exception as e:
        print(f"Fatal error parsing {file_path}: {e}")
        debug_print_file_contents(file_path)
        raise

def compare_xml_structures(reference_file, generated_file):
    """
    Compare XML structures with detailed comparison.
    
    Args:
        reference_file (Path): Path to reference XML file
        generated_file (Path): Path to generated XML file
    
    Raises:
        AssertionError: If XML structures differ
    """
    # Parse structures with additional error handling
    try:
        ref_structure = parse_xml_structure(reference_file)
        gen_structure = parse_xml_structure(generated_file)
    except Exception as e:
        print(f"Error parsing XML files: {e}")
        raise
    
    def normalize_structure(structure):
        """
        Normalize XML structure for comparison.
        
        Args:
            structure (dict): XML structure to normalize
        
        Returns:
            dict: Normalized structure
        """
        if not structure:
            return structure
        
        # Sort children based on tag and attributes
        structure['children'] = sorted(
            structure['children'], 
            key=lambda x: (x['tag'], str(sorted(x['attributes'].items())))
        )
        
        # Normalize text (remove extra whitespace)
        structure['text'] = ' '.join(structure['text'].split())
        
        # Remove empty text
        if not structure['text']:
            structure['text'] = ''
        
        # Recursively normalize children
        for child in structure['children']:
            normalize_structure(child)
        
        return structure

    # Normalize structures
    ref_structure = normalize_structure(ref_structure)
    gen_structure = normalize_structure(gen_structure)
    
    def compare_numeric_values(val1, val2):
        """
        Compare numeric values, treating scientific notation and decimal notation as equivalent.
        
        Args:
            val1 (str): First value to compare
            val2 (str): Second value to compare
        
        Returns:
            bool: True if values are equivalent, False otherwise
        """
        try:
            # Convert both values to floats to handle scientific and decimal notation
            float1 = float(val1)
            float2 = float(val2)
            
            # Compare with a small tolerance to handle floating-point precision
            return abs(float1 - float2) < 1e-10
        except ValueError:
            # If conversion fails, do a string comparison
            return val1 == val2

    def compare_structures(ref, gen, path=''):
        """
        Recursively compare XML structures.
        
        Args:
            ref (dict): Reference structure
            gen (dict): Generated structure
            path (str): Current path in the structure
        
        Raises:
            AssertionError: If structures differ
        """
        # Validate input structures
        assert ref is not None, f"Reference structure is None at path {path}"
        assert gen is not None, f"Generated structure is None at path {path}"
        
        assert ref['tag'] == gen['tag'], f"Tag mismatch at {path}: {ref['tag']} != {gen['tag']}"
        
        # Compare attributes (sorted to handle order differences)
        ref_attrs = sorted(ref['attributes'].items())
        gen_attrs = sorted(gen['attributes'].items())
        
        # Custom comparison for attributes to handle numeric values
        for (ref_key, ref_val), (gen_key, gen_val) in zip(ref_attrs, gen_attrs):
            assert ref_key == gen_key, f"Attribute key mismatch at {path}: {ref_key} != {gen_key}"
            assert compare_numeric_values(ref_val, gen_val), \
                f"Attributes mismatch at {path}/{ref['tag']}: {ref_val} != {gen_val}"
        
        # Compare text content (with numeric comparison)
        ref_text = ' '.join(ref['text'].split())
        gen_text = ' '.join(gen['text'].split())
        assert compare_numeric_values(ref_text, gen_text), \
            f"Text content mismatch at {path}/{ref['tag']}: '{ref['text']}' != '{gen['text']}'"
        
        # Compare children
        assert len(ref['children']) == len(gen['children']), \
            f"Number of children differs at {path}/{ref['tag']}: {len(ref['children'])} != {len(gen['children'])}"
        
        # Recursively compare children
        for i, (ref_child, gen_child) in enumerate(zip(ref['children'], gen['children'])):
            compare_structures(ref_child, gen_child, path=f"{path}/{ref['tag']}[{i}]")
    
    # Perform comparison
    compare_structures(ref_structure, gen_structure)


@pytest.mark.parametrize("example_nr", _get_examples())
def test_generate(capsys, example_nr):
    print(f"Starting test for example number: {example_nr}")
    start_time = time.time()
    
    try:
        root = Path(__file__).parent.parent.parent
        sys.path.append(str(root))
        from FileGenerator import FileGenerator

        # Load JSON schema
        schema_path = root / "schemas" / "topology-schema.json"
        with open(schema_path, 'r') as schema_file:
            topology_schema = json.load(schema_file)

        # Use example_nr for examples
        topology_file = root / "controller_utils" / "examples" / f"{example_nr}" / "topology.yaml"
        output_path = root
        
        print(f"Processing topology file: {topology_file}")
        
        # Validate topology file against JSON schema
        with open(topology_file, 'r') as file:
            topology_data = yaml.safe_load(file)
        
        try:
            # Validate against JSON schema
            jsonschema.validate(instance=topology_data, schema=topology_schema)
        except jsonschema.ValidationError as validation_error:
            pytest.fail(f"Topology file {topology_file} failed schema validation: {validation_error}")

        # Instantiate FileGenerator with verbose logging
        print("Creating FileGenerator...")
        fileGenerator = FileGenerator(topology_file, output_path)

        # Capture and test output of generate_level_0
        print("Generating level 0...")
        fileGenerator.generate_level_0()
        captured = capsys.readouterr()
        assert "error" not in captured.out.lower() and "error" not in captured.err.lower(), \
            f"Error in {str(topology_file)} during generate_level_0"

        # Capture and test output of generate_level_1
        print("Generating level 1...")
        fileGenerator.generate_level_1()

        # Format precice config
        print("Formatting precice config...")
        fileGenerator.format_precice_config()

        captured = capsys.readouterr()
        assert "error" not in captured.out.lower() and "error" not in captured.err.lower(), \
            f"Error in {str(topology_file)} during config formatting"

        # Compare generated precice config with reference files using custom XML comparison
        reference_file = root / "controller_utils" / "examples" / f"{example_nr}" / "precice-config.xml"
        generated_file = root / "_generated" / "precice-config.xml"

        print(f"Reference file: {reference_file}")
        print(f"Generated file: {generated_file}")

        # Check if files exist
        assert reference_file.exists(), f"Reference file does not exist: {reference_file}"
        assert generated_file.exists(), f"Generated file does not exist: {generated_file}"

        # Compare XML structures
        print("Comparing XML structures...")
        compare_xml_structures(reference_file, generated_file)
        
        # Print total test time
        end_time = time.time()
        print(f"Test for example {example_nr} completed in {end_time - start_time:.2f} seconds")
    
    except Exception as e:
        # Catch and print any unexpected errors with full traceback
        print(f"Unexpected error in test_generate for example {example_nr}: {e}")
        traceback.print_exc()
        
        # Print additional context about the error
        print("\nAdditional Error Context:")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        
        raise  # Re-raise to fail the test
