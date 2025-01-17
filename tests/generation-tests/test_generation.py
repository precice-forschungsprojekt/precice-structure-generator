import sys
from pathlib import Path
import pytest

@pytest.mark.parametrize("example_nr", range(1, 9))
def test_generate(capsys, example_nr):
    root = Path(__file__).parent.parent.parent
    sys.path.append(str(root))
    from FileGenerator import FileGenerator

    # Use example_nr directly without an inner loop
    topology_file = root / "controller_utils" / "examples" / f"{example_nr}" / "topology.yaml"
    output_path = root
    fileGenerator = FileGenerator(topology_file, output_path)

    # Capture and test output of generate_level_0
    fileGenerator.generate_level_0()
    captured = capsys.readouterr()
    assert "error" not in captured.out.lower() and "error" not in captured.err.lower(), \
        f"Error in {str(topology_file)}"

    # Capture and test output of generate_level_1
    fileGenerator.generate_level_1()
    captured = capsys.readouterr()
    assert "error" not in captured.out.lower() and "error" not in captured.err.lower(), \
        f"Error in {str(topology_file)}"
