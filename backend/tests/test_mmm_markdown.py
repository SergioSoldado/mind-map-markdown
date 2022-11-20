import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from mmm.markdown import make_graph, graph_to_react_flow


def test_get_graph_valid_dir():
    g = make_graph(Path(__file__).parent / "example")
    pos = nx.spring_layout(g)
    labels = nx.get_node_attributes(g, "label")
    nx.draw(g, pos, labels=labels, with_labels=True)
    plt.show()

    react_flow_graph = graph_to_react_flow(g)
    assert len(react_flow_graph["nodes"]) > 7
    assert "nodes" in react_flow_graph
    assert "edges" in react_flow_graph
