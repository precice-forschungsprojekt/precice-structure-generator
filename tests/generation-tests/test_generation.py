import sys
import os
from pathlib import Path
import pytest
import yaml
import json
import jsonschema
import difflib
import xml.etree.ElementTree as ET


def _get_examples():
    """Get the list of examples as ints in the examples directory"""
    root = Path(__file__).parent.parent.parent
    examples_dir = root / "controller_utils" / "examples"
    return sorted([example.name for example in examples_dir.iterdir() if example.is_dir()])


def parse_xml_structure(file_path):
    """
    Custom XML parsing function that extracts structural information.
    
    Args:
        file_path (Path): Path to the XML file
    
    Returns:
        dict: Nested dictionary representing XML structure
    """
    def clean_text(text):
        """Remove whitespace and normalize text."""
        return text.strip() if text else ''

    def parse_element(lines, start_index):
        """
        Recursively parse XML elements.
        
        Args:
            lines (list): Lines of the XML file
            start_index (int): Starting line index
        
        Returns:
            tuple: (parsed element dict, next line index)
        """
        # Remove leading/trailing whitespace and ignore comments
        while start_index < len(lines):
            line = lines[start_index].strip()
            if line and not line.startswith('<!--'):
                break
            start_index += 1
        
        if start_index >= len(lines):
            return None, start_index
        
        line = lines[start_index].strip()
        
        # Check for opening tag
        if not (line.startswith('<') and not line.startswith('<?') and not line.startswith('<!') and not line.startswith('</')):
            return None, start_index
        
        # Extract tag name and attributes
        tag_parts = line[1:].split('>', 1)[0].split()
        tag_name = tag_parts[0].rstrip('/')
        
        # Parse attributes
        attributes = {}
        for attr in tag_parts[1:]:
            if '=' in attr:
                key, value = attr.split('=', 1)
                attributes[key] = value.strip('\'"')
        
        # Check if self-closing tag
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
        
        start_index += 1
        
        # Parse children and text
        while start_index < len(lines):
            line = lines[start_index].strip()
            
            # Check for closing tag
            if line.startswith(f'</{tag_name}>'):
                return element, start_index + 1
            
            # Check for nested element
            if line.startswith('<') and not line.startswith('<!--'):
                child, start_index = parse_element(lines, start_index)
                if child:
                    element['children'].append(child)
                continue
            
            # Accumulate text content
            if line and not line.startswith('<!--'):
                element['text'] += line + ' '
            
            start_index += 1
        
        return element, start_index

    # Read file and parse
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Remove XML declaration and comments
    lines = [line for line in lines if not line.strip().startswith('<?') and not line.strip().startswith('<!--')]
    
    # Parse root element
    root, _ = parse_element(lines, 0)
    return root

def compare_xml_structures(reference_file, generated_file):
    """
    Compare XML structures with detailed comparison.
    
    Args:
        reference_file (Path): Path to reference XML file
        generated_file (Path): Path to generated XML file
    
    Raises:
        AssertionError: If XML structures differ
    """
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
        
        # Sort children by tag name
        structure['children'] = sorted(
            structure['children'], 
            key=lambda x: (x['tag'], str(sorted(x['attributes'].items())))
        )
        
        # Normalize text
        structure['text'] = structure['text'].strip()
        
        # Recursively normalize children
        for child in structure['children']:
            normalize_structure(child)
        
        return structure

    # Parse and normalize XML structures
    ref_structure = normalize_structure(parse_xml_structure(reference_file))
    gen_structure = normalize_structure(parse_xml_structure(generated_file))
    
    # Custom comparison function
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
        assert ref['tag'] == gen['tag'], f"Tag mismatch at {path}: {ref['tag']} != {gen['tag']}"
        
        # Compare attributes
        assert set(ref['attributes'].items()) == set(gen['attributes'].items()), \
            f"Attributes mismatch at {path}/{ref['tag']}: {ref['attributes']} != {gen['attributes']}"
        
        # Compare text content (ignoring whitespace)
        assert ref['text'].replace(' ', '') == gen['text'].replace(' ', ''), \
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
    root = Path(__file__).parent.parent.parent
    sys.path.append(str(root))
    from FileGenerator import FileGenerator

    # Load JSON schema
    schema_path = root / "schemas" / "topology-schema.json"
    with open(schema_path, 'r') as schema_file:
        topology_schema = json.load(schema_file)

    # Use example_nr for 8 examples
    topology_file = root / "controller_utils" / "examples" / f"{example_nr}" / "topology.yaml"
    output_path = root
    
    # Validate topology file against JSON schema
    with open(topology_file, 'r') as file:
        topology_data = yaml.safe_load(file)
    
    try:
        # Validate against JSON schema
        jsonschema.validate(instance=topology_data, schema=topology_schema)
    except jsonschema.ValidationError as validation_error:
        pytest.fail(f"Topology file {topology_file} failed schema validation: {validation_error}")

    fileGenerator = FileGenerator(topology_file, output_path)

    # Capture and test output of generate_level_0
    fileGenerator.generate_level_0()
    captured = capsys.readouterr()
    assert "error" not in captured.out.lower() and "error" not in captured.err.lower(), \
        f"Error in {str(topology_file)}"

    # Capture and test output of generate_level_1
    fileGenerator.generate_level_1()

    fileGenerator.format_precice_config(output_path)

    captured = capsys.readouterr()
    assert "error" not in captured.out.lower() and "error" not in captured.err.lower(), \
        f"Error in {str(topology_file)}"

    # Compare generated precice config with reference files using custom XML comparison
    reference_file = root / "controller_utils" / "examples" / f"{example_nr}" / "precice-config.xml"
    generated_file = root / "_generated" / "precice-config.xml"

    compare_xml_structures(reference_file, generated_file)
