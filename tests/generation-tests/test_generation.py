import sys
import os
from pathlib import Path
import pytest
import yaml
import json
import jsonschema


def _get_examples():
    """Get the list of examples as ints in the examples directory"""
    root = Path(__file__).parent.parent.parent
    examples_dir = root / "controller_utils" / "examples"
    return sorted([example.name for example in examples_dir.iterdir() if example.is_dir()])


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

    # Compare generated precice config with reference files
    reference_file = root / "controller_utils" / "examples" / f"{example_nr}" / "precice-config.xml"
    generated_file = root / "_generated" / "precice-config.xml"
    
    with open(reference_file, 'r') as ref_file:
        reference_lines = ref_file.readlines()
    
    with open(generated_file, 'r') as gen_file:
        generated_lines = gen_file.readlines()

    # Compare line by line, ignoring leading/trailing whitespace and extra spaces within lines
    for ref_line, gen_line in zip(reference_lines, generated_lines):
        # Ignore empty lines
        if ref_line.strip() == "" or gen_line.strip() == "":
            continue
        assert ''.join(ref_line.split()) == ''.join(gen_line.split()), \
            f"Difference found:\nReference: {ref_line}\nGenerated: {gen_line}"
