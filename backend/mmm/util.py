import re
from pathlib import Path


def find_line_in_file(f_path: Path, pattern: str) -> int:
    """
    Find the line number of a pattern in a file
    Args:
        f_path: Path to the file
        pattern: Pattern of line to search for

    Returns: Line if pattern found, 1 otherwise

    """
    with open(f_path, "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if re.match(pattern, line):
                return i + 1
    return 1
