import pytest

@pytest.fixture
def generated_config():
    """Fixture to load the generated configuration file"""
    import os
    
    # Update this path to the actual location of your generated config
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        '_generated', 
        'precice-config.xml'
    )
    
    with open(config_path, 'r') as f:
        return f.read()

def test_configuration(generated_config):
    """Verify various deprecated tags and attributes are removed or replaced"""
    solver_interface_removed = True
    m2n_replaced = True
    use_mesh_replaced = True
    extrapolation_order_removed = True
    timing_removed = True

    for line in generated_config.splitlines():
        # Test for solver interface tags
        if '<solver-interface' in line or '</solver-interface>' in line:
            solver_interface_removed = False
        # Test for deprecated m2n attributes
        if 'm2n' in line and ('from=' in line or 'to=' in line):
            m2n_replaced = False
        # Test for deprecated use-mesh attributes
        if 'use-mesh provide=' in line or '<use-mesh' in line:
            use_mesh_replaced = False
        # Test for extrapolation order
        if '<extrapolation-order' in line:
            extrapolation_order_removed = False
        # Test for timing attributes in mapping configuration
        if 'timing="initial"' in line:
            timing_removed = False

    # Asserting and printing custom messages
    assert solver_interface_removed, "Solver interface tags should be removed"
    print("Solver interface tags removed successfully.")

    assert m2n_replaced, "Deprecated 'm2n:from' and 'm2n:to' attributes should be replaced"
    print("Deprecated 'm2n:from' and 'm2n:to' attributes replaced successfully.")

    assert use_mesh_replaced, "Deprecated 'use-mesh provide' should be replaced"
    print("Deprecated 'use-mesh provide' attributes and tags replaced successfully.")

    assert extrapolation_order_removed, "Extrapolation order should be removed"
    print("Extrapolation order tags removed successfully.")

    assert timing_removed, "Timing attributes in the mapping configuration should be removed"
    print("Timing attributes in the mapping configuration removed successfully.")

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
