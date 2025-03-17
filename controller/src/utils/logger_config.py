import logging 
from logging.handlers import TimedRotatingFileHandler

from flask.logging import default_handler


def config_logger(app, level=0):
    handler = TimedRotatingFileHandler('/app/logs/logs.log', when='midnight', backupCount=7)
    handler.suffix = '%d-%m-%Y.log'

    app.logger.removeHandler(default_handler)
    formatter = logging.Formatter('[%(asctime)s] - [%(name)s] - %(levelname)s: %(message)s')

    handler.setFormatter(formatter)
    app.logger.root.addHandler(handler)
    app.logger.root.setLevel(level)
    app.logger.setLevel(logging.ERROR)

    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(level)
