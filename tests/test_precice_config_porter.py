import os
import re
import pytest
import tempfile
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from PreciceConfigPorter import port_v2_to_v3, XMLTransformer, xml_transform, get_attributes

class MockLogger:
    def __init__(self):
        self.info_messages = []
        self.error_messages = []
    
    def info(self, message):
        self.info_messages.append(message)
    
    def error(self, message):
        self.error_messages.append(message)

def read_file_content(file_path):
    """Read and return file content"""
    with open(file_path, 'r') as f:
        return f.read()

def test_xml_transformer_rename_tag():
    """Test renaming XML tags"""
    line = '<use-mesh name="Mesh1" provide="yes"/>'
    transformer = XMLTransformer(line)
    result = transformer.rename_tag('use-mesh', 'provide-mesh').get_line()
    assert '<provide-mesh' in result
    assert 'name="Mesh1"' in result
    assert 'provide="yes"' in result

def test_xml_transformer_remove_attribute():
    """Test removing attributes from XML tags"""
    line = '<use-mesh name="Mesh1" provide="yes"/>'
    transformer = XMLTransformer(line)
    result = transformer.remove_attribute('provide').get_line()
    assert '<use-mesh' in result
    assert 'name="Mesh1"' in result
    assert 'provide=' not in result

def test_xml_transformer_add_attribute():
    """Test adding attributes to XML tags"""
    line = '<mesh name="Mesh1"/>'
    transformer = XMLTransformer(line)
    result = transformer.add_attribute('dimensions', '3').get_line()
    assert '<mesh' in result
    assert 'name="Mesh1"' in result
    assert 'dimensions="3"' in result

def test_xml_transformer_replace_attribute():
    """Test replacing attribute names"""
    line = '<m2n:sockets from="Participant1" to="Participant2"/>'
    transformer = XMLTransformer(line)
    result = transformer.replace_attribute('from', 'acceptor').replace_attribute('to', 'connector').get_line()
    assert 'acceptor="Participant1"' in result
    assert 'connector="Participant2"' in result
    assert 'from=' not in result
    assert 'to=' not in result

def test_port_v2_to_v3_mesh_dimensions():
    """Test adding dimensions to mesh tags"""
    input_xml = """<?xml version="1.0"?>
    <solver-interface dimensions="3">
        <mesh name="Mesh1">
            <use-data name="Data1"/>
        </mesh>
    </solver-interface>
    """
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xml') as input_file, \
         tempfile.NamedTemporaryFile(mode='r', delete=False, suffix='.xml') as output_file:
        input_file.write(input_xml)
        input_file.close()
        output_file.close()
        
        logger = MockLogger()
        port_v2_to_v3(logger, input_file.name, output_file.name)
        
        # Read output content
        output_content = read_file_content(output_file.name)
        
        # Check mesh dimensions
        assert 'mesh name="Mesh1" dimensions="3"' in output_content
        
        # Clean up temp files
        os.unlink(input_file.name)
        os.unlink(output_file.name)

def test_port_v2_to_v3_solver_interface_attributes():
    """Test moving solver interface attributes"""
    input_xml = """<?xml version="1.0"?>
    <solver-interface dimensions="2" experimental="true" sync-mode="serial">
        <mesh name="Mesh1">
            <use-data name="Data1"/>
        </mesh>
    </solver-interface>
    """
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xml') as input_file, \
         tempfile.NamedTemporaryFile(mode='r', delete=False, suffix='.xml') as output_file:
        input_file.write(input_xml)
        input_file.close()
        output_file.close()
        
        logger = MockLogger()
        port_v2_to_v3(logger, input_file.name, output_file.name)
        
        # Read output content
        output_content = read_file_content(output_file.name)
        
        # Check precice-configuration attributes
        assert 'experimental="true"' in output_content
        
        # Check profiling tag
        assert '<profiling sync-mode="serial"/>' in output_content
        
        # Clean up temp files
        os.unlink(input_file.name)
        os.unlink(output_file.name)

def test_port_v2_to_v3_mesh_tag_transformations():
    """Test various mesh tag transformations"""
    input_xml = """<?xml version="1.0"?>
    <solver-interface>
        <mesh name="Mesh1">
            <use-mesh name="Mesh1" provide="yes"/>
            <read-data: name="Data1" waveform-order="1"/>
        </mesh>
    </solver-interface>
    """
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xml') as input_file, \
         tempfile.NamedTemporaryFile(mode='r', delete=False, suffix='.xml') as output_file:
        input_file.write(input_xml)
        input_file.close()
        output_file.close()
        
        logger = MockLogger()
        port_v2_to_v3(logger, input_file.name, output_file.name)
        
        # Read output content
        output_content = read_file_content(output_file.name)
        
        # Check use-mesh transformation
        assert '<provide-mesh' in output_content
        
        # Check read-data transformation
        assert 'data:scalar/vector' in output_content
        assert 'waveform-degree="1"' in output_content
        assert 'waveform-order=' not in output_content
        
        # Clean up temp files
        os.unlink(input_file.name)
        os.unlink(output_file.name)

def test_port_v2_to_v3_m2n_transformations():
    """Test m2n attribute transformations"""
    input_xml = """<?xml version="1.0"?>
    <precice-configuration>
        <m2n:sockets from="Participant1" to="Participant2"/>
    </precice-configuration>
    """
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xml') as input_file, \
         tempfile.NamedTemporaryFile(mode='r', delete=False, suffix='.xml') as output_file:
        input_file.write(input_xml)
        input_file.close()
        output_file.close()
        
        logger = MockLogger()
        port_v2_to_v3(logger, input_file.name, output_file.name)
        
        # Read output content
        output_content = read_file_content(output_file.name)
        
        # Check m2n attribute transformation
        assert 'acceptor="Participant1"' in output_content
        assert 'connector="Participant2"' in output_content
        assert 'from=' not in output_content
        assert 'to=' not in output_content
        
        # Clean up temp files
        os.unlink(input_file.name)
        os.unlink(output_file.name)

def test_port_v2_to_v3_mapping_constraints():
    """Test mapping constraint transformations"""
    input_xml = """<?xml version="1.0"?>
    <precice-configuration>
        <mapping:nearest-neighbor constraint="scaled-consistent"/>
    </precice-configuration>
    """
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xml') as input_file, \
         tempfile.NamedTemporaryFile(mode='r', delete=False, suffix='.xml') as output_file:
        input_file.write(input_xml)
        input_file.close()
        output_file.close()
        
        logger = MockLogger()
        port_v2_to_v3(logger, input_file.name, output_file.name)
        
        # Read output content
        output_content = read_file_content(output_file.name)
        
        # Check mapping constraint transformation
        assert 'constraint="scaled-consistent-surface"' in output_content
        
        # Clean up temp files
        os.unlink(input_file.name)
        os.unlink(output_file.name)

def test_port_v2_to_v3_min_iterations():
    """Test min-iteration-convergence-measure transformation"""
    input_xml = """<?xml version="1.0"?>
    <precice-configuration>
        <min-iteration-convergence-measure min-iterations="5" data="some-data"/>
    </precice-configuration>
    """
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xml') as input_file, \
         tempfile.NamedTemporaryFile(mode='r', delete=False, suffix='.xml') as output_file:
        input_file.write(input_xml)
        input_file.close()
        output_file.close()
        
        logger = MockLogger()
        port_v2_to_v3(logger, input_file.name, output_file.name)
        
        # Read output content
        output_content = read_file_content(output_file.name)
        
        # Check min-iterations transformation
        assert '<min-iterations value="5"/>' in output_content
        
        # Clean up temp files
        os.unlink(input_file.name)
        os.unlink(output_file.name)

def test_get_attributes():
    """Test attribute extraction"""
    line = '<solver-interface dimensions="3" experimental="true"/>'
    attributes = get_attributes(line)
    
    assert attributes == {
        'dimensions': '3',
        'experimental': 'true'
    }
