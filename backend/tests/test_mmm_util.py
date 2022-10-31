from pathlib import Path
from mmm.util import find_line_in_file


def test_find_line_in_file():
    f_path = Path(__file__).parent / "example" / "a.md"
    assert f_path.is_file(), f"{f_path} is not a file"
    assert find_line_in_file(f_path, "# A") == 1
    assert find_line_in_file(f_path, "## AA") == 3
    assert find_line_in_file(f_path, "### AAA") == 5
    assert find_line_in_file(f_path, "#### AAAA") == 7
