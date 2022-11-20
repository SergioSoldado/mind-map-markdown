import argparse
import logging
import subprocess
import time
from pathlib import Path
from threading import Thread

import inotify.adapters
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from mmm.markdown import make_graph, graph_to_react_flow, GraphControls
from mmm.util import find_line_in_file

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
_this_dir = Path(__file__).parent
app = Flask(__name__, instance_relative_config=True)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
_graph_controls = GraphControls()
force_emit = False


def create_graph():
    global _markdown_root, _graph_controls
    g = make_graph(_markdown_root, graph_controls=_graph_controls)
    return graph_to_react_flow(g)


def task():
    """
    Watch for changes in the root directory and emit a graph to the client
    """
    assert _markdown_root.is_dir()
    i = inotify.adapters.InotifyTree(str(_markdown_root))
    while True:
        for event in i.event_gen(yield_nones=False):
            (_, type_names, path, filename) = event
            if "IN_CLOSE_WRITE" in type_names:
                log.debug(f"File {path}/{filename} was modified")
                socketio.emit("graph", create_graph())
                break
        time.sleep(0.2)


@app.route("/graph/controls", methods=["POST"])
def graph_controls():
    """
    Endpoint to set custom controls that control graph layout, depth, etc
    """
    global _graph_controls, force_emit
    _graph_controls = GraphControls.from_dict(request.json)
    log.debug(f"Changed depth to {_graph_controls.depth}")
    socketio.emit("graph", create_graph())
    return "", 201


@app.route("/graph")
def graph():
    """
    Rest endpoint that return a graph of the markdown files in the root directory
    Returns:

    """
    return create_graph()


@app.route("/onClick", methods=["POST"])
def clicked():
    content = request.json
    log.debug(f'Clicked on {content["id"]}')
    g = create_graph()
    for node in g["nodes"]:
        if node["id"] == content["id"]:
            log.debug(f'Found {node["id"]}')
            f_path = _markdown_root / node["id"]
            if f_path.is_file():
                log.debug(f"Opening {f_path}")
                subprocess.call(f"pycharm {f_path.absolute()}", shell=True)
            else:
                file, line = content["id"].split("#")
                f_path = _markdown_root / file
                line = rf"^ *# *{line}"
                line = find_line_in_file(f_path, line)
                log.debug(f"Opening {f_path}:{line}")
                subprocess.call(
                    f"pycharm --line {line} {f_path.absolute()}", shell=True
                )
            break
    return "", 201


@socketio.on("connect")
def connect():
    log.debug(f"Client connected {request.sid}")
    assert _markdown_root.is_dir, f"{_markdown_root} is not a directory"
    emit("graph", create_graph())


@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the server"""
    log.debug(f"Client disconnected {request.sid}")
    # emit("disconnect", f"user {request.sid} disconnected", broadcast=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mind Map Markdown")
    parser.add_argument("--root-dir", type=Path, required=True)
    args = parser.parse_args()

    _markdown_root = args.root_dir.resolve().absolute()
    assert _markdown_root.is_dir(), f"{_markdown_root} is not a directory"
    assert (
        _this_dir not in _markdown_root.parents
    ), f"{_markdown_root} can't be a subdirectory of project root"

    thread = Thread(target=task)
    thread.start()
    socketio.run(app, debug=False, port=5000)
