import pytest
from pathlib import Path
from mmm.markdown import get_graph


def test_get_graph_bad_path():
    with pytest.raises(AssertionError):
        get_graph(Path("bad_path"))


def test_get_graph_valid_dir():
    g = get_graph(Path(__file__).parent / "example")
    assert "nodes" in g
    assert "edges" in g
    assert len(g["nodes"]) > 7
