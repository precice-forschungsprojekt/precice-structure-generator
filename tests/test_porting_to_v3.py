import pytest

def test_no_solver_interface_tags(generated_config):
    """Verify no <solver-interface> tags remain in the configuration"""
    assert '<solver-interface' not in generated_config, "Solver interface tags should be removed"

def test_no_deprecated_m2n_attributes(generated_config):
    """Verify m2n attributes 'from' and 'to' are replaced"""
    if 'm2n=' in generated_config:
        assert 'from=' not in generated_config, "Deprecated 'm2n:from' attribute should be replaced"
        assert 'to=' not in generated_config, "Deprecated 'm2n:to' attribute should be replaced"

def test_no_deprecated_use_mesh_attributes(generated_config):
    """Verify 'provide' attribute in use-mesh is replaced"""
    assert 'use-mesh provide=' not in generated_config, "Deprecated 'use-mesh provide' should be replaced"
    assert '<use-mesh' not in generated_config, "Use-mesh tags should be replaced with provide-mesh/receive-mesh"




def test_no_extrapolation_order(generated_config):
    """Verify extrapolation order is removed"""
    assert '<extrapolation-order' not in generated_config, "Extrapolation order should be removed"


@pytest.fixture
def generated_config():
    """Fixture to load the generated configuration file"""
    import os
    
    # Update this path to the actual location of your generated config
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        '_generated', 
        'config', 
        'precice-config.xml'
    )
    
    with open(config_path, 'r') as f:
        return f.read()



# Add this at the end of the file
if __name__ == "__main__":
    import sys
    import os

    # Add the project root to the Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)

    try:
        # Attempt to run the tests
        import pytest
        
        # Customize the pytest arguments
        pytest_args = [
            __file__,  # Current file
            '-v',      # Verbose output
            '-s'       # Show print statements
        ]
        
        # Run the tests
        exit_code = pytest.main(pytest_args)
        
        # Exit with the pytest exit code
        sys.exit(exit_code)
    
    except ImportError:
        print("Error: pytest is not installed. Please install it using 'pip install pytest'")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Generated configuration file not found. Please ensure the file exists at:")
        print(os.path.join(project_root, '_generated', 'config', 'precice-config.xml'))
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)