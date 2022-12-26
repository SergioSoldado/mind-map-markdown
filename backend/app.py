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

from mmm.markdown import make_graph, graph_to_react_flow, GraphOptions
from mmm.util import find_line_in_file

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
_this_dir = Path(__file__).parent
app = Flask(__name__, instance_relative_config=True)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
_graph_opt = None
force_emit = False


def create_graph():
    global _graph_opt
    g = make_graph(opt=_graph_opt)
    return graph_to_react_flow(g=g, opt=_graph_opt)


def task():
    """
    Watch for changes in the root directory and emit a graph to the client
    """
    i = inotify.adapters.InotifyTree(str(root_dir))
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
    global _graph_opt, force_emit
    _graph_opt.update(**request.json)
    log.debug(f"Graph options: {_graph_opt.to_json(indent=2)}")
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
            f_path = root_dir / node["id"]
            if f_path.is_file():
                log.debug(f"Opening {f_path}")
                subprocess.call(f"pycharm {f_path.absolute()}", shell=True)
            else:
                file, line = content["id"].split("#")
                f_path = root_dir / file
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
    assert _graph_opt.root_dir.is_dir, f"{root_dir} is not a directory"
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

    root_dir = args.root_dir.resolve().absolute()
    assert root_dir.is_dir(), f"{root_dir} is not a directory"
    assert (
        _this_dir not in root_dir.parents
    ), f"{root_dir} can't be a subdirectory of project root"

    _graph_opt = GraphOptions(root_dir=root_dir)

    thread = Thread(target=task)
    thread.start()
    socketio.run(app, debug=False, port=5000)
