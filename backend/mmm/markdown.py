import glob
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import marko
import networkx as nx
from bs4 import BeautifulSoup as Soup
from dataclasses_json import dataclass_json

log = logging.getLogger(__name__)


@dataclass_json
@dataclass
class GraphControls:
    depth: int = 1


def grow_graph(
    soup: Soup, root_node_id: str, g: nx.Graph, max_depth: Optional[int] = 6
):
    stack = []
    node_cnt = 0
    for element in soup:
        # element: PageElement
        try:
            t = ["h1", "h2", "h3", "h4", "h5", "h6"].index(element.name) + 1
        except ValueError:
            continue
        log.debug(f"t={t} max_depth={max_depth}")
        node_id = f"{root_node_id}.{node_cnt}"
        if t <= max_depth:
            g.add_node(node_id, label=element.text)
        while len(stack) > 0 and t <= stack[-1][0]:
            stack.pop()
        if t <= max_depth:
            if len(stack) > 0:
                g.add_edge(stack[-1][2], node_id)
            else:
                g.add_edge(root_node_id, node_id)
            stack.append((t, element, node_id))
            node_cnt += 1


def make_graph(
    root_dir: Path, graph_controls: Optional[GraphControls] = None
) -> nx.Graph:
    assert root_dir.is_dir(), f"{root_dir} is not a directory"
    if graph_controls is None:
        graph_controls = GraphControls()
    md_files = list(glob.iglob(f"{root_dir}/**/*.md", recursive=True))
    g = nx.Graph()
    for md_file in md_files:
        node_id = str(Path(md_file).relative_to(root_dir))
        g.add_node(node_id, label=node_id)
    for md_file in md_files:
        md_file_path = Path(md_file)
        node_id = str(md_file_path.relative_to(root_dir))
        soup = Soup(marko.convert(md_file_path.read_text()), features="html.parser")
        grow_graph(soup, node_id, g, graph_controls.depth)
        for a in soup.findAll("a"):
            dst = a.get("href")
            path = (md_file_path.parent / dst).resolve()
            if not path.is_file():
                log.error(f"File {path} does not exist")
                continue
            other_node_id = str(path.relative_to(root_dir))
            g.add_edge(node_id, other_node_id)
    return g


def graph_to_react_flow(g: nx.Graph, pos: Optional[dict] = None):
    labels = nx.get_node_attributes(g, "label")
    if pos is None:
        pos = nx.spring_layout(G=g, seed=0)
    nodes = []
    for n in g.nodes:
        nodes.append(
            {
                "id": n,
                "data": {"label": labels[n]},
                "position": {"x": pos[n][0], "y": pos[n][1]},
            }
        )
    edges = []
    for e in g.edges:
        edges.append({"id": f"{len(edges)}", "source": e[0], "target": e[1]})
    return {"nodes": nodes, "edges": edges}
