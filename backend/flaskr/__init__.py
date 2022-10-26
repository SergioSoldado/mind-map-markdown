import logging
import time
from pathlib import Path
from threading import Thread

import inotify.adapters
from flask import Flask, session, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from flaskr.markdown import get_graph

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
_root_dir = Path(__file__).parents[1]
_markdown_root = Path('/home/serj/projects/example')
assert _markdown_root.is_dir()

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")


def task():
    i = inotify.adapters.InotifyTree(str(_markdown_root))
    while True:
        for event in i.event_gen(yield_nones=False):
            (_, type_names, path, filename) = event
            if 'IN_CLOSE_WRITE' in type_names:
                log.debug(f'File {path}/{filename} was modified')
                socketio.emit('graph', get_graph(_markdown_root))
                break
        time.sleep(0.2)


# thread = socketio.start_background_task(task)
thread = Thread(target=task)
thread.start()


# a simple page that says hello
@app.route('/graph')
def graph():
    return get_graph(_markdown_root)


@socketio.event
def my_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on("connect")
def connect():
    print(request.sid)
    print("Client connected")
    emit('graph', get_graph(_markdown_root))


@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the server"""
    print("user disconnected")
    emit("disconnect", f"user {request.sid} disconnected", broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
