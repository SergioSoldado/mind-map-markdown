import glob
import json
import logging
from pathlib import Path
from typing import Optional

import marko
import networkx as nx
from bs4 import BeautifulSoup as Soup

log = logging.getLogger(__name__)


class GraphOptions:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == "root_dir":
                value = Path(value)
            setattr(self, key, value)
        if "root_dir" not in kwargs:
            self.root_dir = None
        if "depth" not in kwargs:
            self.depth = 1
        if "layout" not in kwargs:
            self.layout = "spring"
        if "manual_layout" not in kwargs:
            self.manual_layout = None

    def to_json(self, indent=None):
        res = self.__dict__.copy()
        if res["root_dir"] is not None:
            res["root_dir"] = str(res["root_dir"])
        return json.dumps(res, indent=indent)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


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


def make_graph(opt: GraphOptions) -> nx.Graph:
    assert opt.root_dir.is_dir(), f"{opt.root_dir} is not a directory"
    md_files = list(glob.iglob(f"{opt.root_dir}/**/*.md", recursive=True))
    g = nx.Graph()
    for md_file in md_files:
        node_id = str(Path(md_file).relative_to(opt.root_dir))
        g.add_node(node_id, label=node_id)
    for md_file in md_files:
        md_file_path = Path(md_file)
        node_id = str(md_file_path.relative_to(opt.root_dir))
        soup = Soup(marko.convert(md_file_path.read_text()), features="html.parser")
        grow_graph(soup, node_id, g, opt.depth)
        for a in soup.findAll("a"):
            dst = a.get("href")
            path = (md_file_path.parent / dst).resolve()
            if not path.is_file():
                log.error(f"File {path} does not exist")
                continue
            other_node_id = str(path.relative_to(opt.root_dir))
            g.add_edge(node_id, other_node_id)
    return g


def graph_to_react_flow(g: nx.Graph, opt: Optional[GraphOptions] = None):
    labels = nx.get_node_attributes(g, "label")
    if opt is None:
        opt = GraphOptions()
    if opt.layout == "spring":
        pos = nx.spring_layout(G=g, seed=0)
    elif opt.layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G=g)
    elif opt.layout == "circular":
        pos = nx.circular_layout(G=g)
    elif opt.layout == "bipartite":
        pos = nx.bipartite_layout(G=g)
    elif opt.layout == "spectral":
        pos = nx.spectral_layout(G=g)
    elif opt.layout == "shell":
        pos = nx.shell_layout(G=g)
    elif opt.layout == "fruchterman_reingold":
        pos = nx.fruchterman_reingold_layout(G=g)
    else:
        log.warning(f"Unknown layout {opt.layout}")
        pos = nx.spring_layout(G=g, seed=0)
    assert pos is not None
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
