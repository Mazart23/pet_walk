import threading

from src import app
from src.utils.algorithm import load_graph
from src.utils.apps import Services


if __name__ == '__main__':
    threading.Thread(target=load_graph, daemon=True).start()
    app.run(host="0.0.0.0", port=Services.CONTROLLER.port, debug=True)
