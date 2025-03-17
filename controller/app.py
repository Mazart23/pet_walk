from src import app
from src.utils.apps import Services


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=Services.CONTROLLER.port, debug=True)
