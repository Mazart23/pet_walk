import os

from src import app, socketio
from src.utils.apps import Services


if __name__ == '__main__':
    socketio.app.run(app, host="0.0.0.0", port=Services.NOTIFIER.port, debug=True, log=open(os.devnull, 'w'))
