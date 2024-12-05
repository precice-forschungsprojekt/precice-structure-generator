import pytest
import sys
sys.path.append('validation')
from validate_config import convert_xml_to_json, load_schema, validate_config

# Test cases for validate_config.py

def test_convert_xml_to_json():
    # XML content to be tested
    xml_content = '''<?xml version="1.0" encoding="UTF-8" ?>
<precice-configuration>
  <log>
    <sink
      filter="%Severity% > debug"
      format="---[precice] %ColorizedSeverity% %Message%"
      enabled="true" />
  </log>

  <data:scalar name="Color" />

  <mesh name="Generator-Mesh" dimensions="2">
    <use-data name="Color" />
  </mesh>

  <mesh name="Propagator-Mesh" dimensions="2">
    <use-data name="Color" />
  </mesh>

  <participant name="Generator">
    <provide-mesh name="Generator-Mesh" />
    <write-data name="Color" mesh="Generator-Mesh" />
  </participant>

  <participant name="Propagator">
    <receive-mesh name="Generator-Mesh" from="Generator" />
    <provide-mesh name="Propagator-Mesh" />
    <mapping:nearest-neighbor
      direction="read"
      from="Generator-Mesh"
      to="Propagator-Mesh"
      constraint="consistent" />
    <read-data name="Color" mesh="Propagator-Mesh" />
  </participant>

  <m2n:sockets acceptor="Generator" connector="Propagator" exchange-directory=".." />

  <coupling-scheme:serial-explicit>
    <participants first="Generator" second="Propagator" />
    <time-window-size value="0.01" />
    <max-time value="0.3" />
    <exchange data="Color" mesh="Generator-Mesh" from="Generator" to="Propagator" />
  </coupling-scheme:serial-explicit>
</precice-configuration>'''

    # Expected JSON structure
    expected_json = {
        'precice-configuration': {
            'log': {
                'sink': {
                    '@filter': '%Severity% > debug',
                    '@format': '---[precice] %ColorizedSeverity% %Message%',
                    '@enabled': 'true'
                }
            },
            'data:scalar': {
                '@name': 'Color'
            },
            'mesh': [
                {
                    '@name': 'Generator-Mesh',
                    '@dimensions': '2',
                    'use-data': [{
                        '@name': 'Color'
                    }]
                },
                {
                    '@name': 'Propagator-Mesh',
                    '@dimensions': '2',
                    'use-data': [{
                        '@name': 'Color'
                    }]
                }
            ],
            'participant': [
                {
                    '@name': 'Generator',
                    'provide-mesh': [{
                        '@name': 'Generator-Mesh'
                    }],
                    'write-data': [{
                        '@name': 'Color',
                        '@mesh': 'Generator-Mesh'
                    }]
                },
                {
                    '@name': 'Propagator',
                    'receive-mesh': [{
                        '@name': 'Generator-Mesh',
                        '@from': 'Generator'
                    }],
                    'provide-mesh': [{
                        '@name': 'Propagator-Mesh'
                    }],
                    'mapping:nearest-neighbor': {
                        '@direction': 'read',
                        '@from': 'Generator-Mesh',
                        '@to': 'Propagator-Mesh',
                        '@constraint': 'consistent'
                    },
                    'read-data': [{
                        '@name': 'Color',
                        '@mesh': 'Propagator-Mesh'
                    }]
                }
            ],
            'm2n:sockets': {
                '@acceptor': 'Generator',
                '@connector': 'Propagator',
                '@exchange-directory': '..'
            },
            'coupling-scheme:serial-explicit': {
                'participants': {
                    '@first': 'Generator',
                    '@second': 'Propagator'
                },
                'time-window-size': {
                    '@value': '0.01'
                },
                'max-time': {
                    '@value': '0.3'
                },
                'exchange': [{
                    '@data': 'Color',
                    '@mesh': 'Generator-Mesh',
                    '@from': 'Generator',
                    '@to': 'Propagator'
                }]
            }
        }
    }

    # Use a temporary file to test the function
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(xml_content.encode('utf-8'))
        tmp_file_path = tmp_file.name

    try:
        # Test the function with the temporary file path
        assert convert_xml_to_json(tmp_file_path) == expected_json
    finally:
        # Clean up the temporary file
        os.remove(tmp_file_path)


def test_load_schema():
    # Test loading a schema, assuming a valid schema file is present.
    schema_path = "schemas/precice-config-schema.json"
    try:
        schema = load_schema(schema_path)
        assert isinstance(schema, dict)
    except Exception as e:
        pytest.fail(f"load_schema() raised an exception: {e}")


def test_validate_config():
    # Test validating a config against a schema.
    json_data = {'root': {'element': 'value'}}
    schema = {'type': 'object', 'properties': {'root': {'type': 'object', 'properties': {'element': {'type': 'string'}}}}}
    assert validate_config(json_data, schema) is True


def test_broken_precice_config():
    # Load the broken precice configuration XML file
    with open(os.path.join(os.path.dirname(__file__), 'broken_precice_config.xml'), 'r') as file:
        xml_content = file.read()
    
    # Convert XML to JSON
    json_content = convert_xml_to_json(xml_content)
    
    # Load the schema
    schema = load_schema()
    
    # Validate the configuration and assert it returns false
    assert not validate_config(json_content, schema), "The broken config should not validate successfully"
