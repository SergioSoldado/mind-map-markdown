import logging
from glob import glob
from pathlib import Path
from typing import Dict, Union

import marko
import networkx as nx
from bs4 import BeautifulSoup as Soup, PageElement

log = logging.getLogger(__name__)


def get_md_soup(md_file: Path) -> Soup:
    return Soup(marko.convert(md_file.read_text()), features="html.parser")


def get_stew(root_dir: Path) -> Dict[Path, Soup]:
    return {
        Path(p): get_md_soup(Path(p))
        for p in glob(f"{root_dir}/**/*.md", recursive=True)
    }


def get_soup_headers(soup: Soup):
    return list(soup.findAll("h1")) + list(soup.findAll("h2"))


def traverse_soup_by_name(
    root: Path, node: Union[Dict[Path, Soup], PageElement], g: nx.Graph
):
    if isinstance(node, dict):
        for filename, soup in node.items():
            soup: Soup
            filename: Path
            k = str(filename.relative_to(root))
            if k not in g.nodes:
                g.add_node(k, label=k)
            for i in get_soup_headers(soup):
                ki = f"{k}#{i.text}"
                g.add_node(ki, label=i.text)
                g.add_edge(k, ki, color="red")
            for i in soup.findAll("a"):
                dst = i.get("href")
                path = (Path(filename.parent) / dst).resolve()
                if not path.is_file():
                    log.error(f"File {path} does not exist")
                    continue
                k2 = str(path.relative_to(root))
                g.add_node(k2, label=k2)
                g.add_edge(k, k2)


def get_graph(root_dir: Path) -> dict:
    assert root_dir.is_dir(), f"{root_dir} is not a directory"
    g = nx.Graph()
    stew = get_stew(root_dir)
    traverse_soup_by_name(root_dir, stew, g)
    labels = nx.get_node_attributes(g, "label")
    pos = nx.kamada_kawai_layout(G=g)
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
