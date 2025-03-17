import os
from logging import DEBUG

from flask import Flask, Blueprint
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from .utils.websocket import Websocket
from .utils.logger_config import config_logger


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

CORS(app, resources={r"/*":{"origins":"*"}})
config_logger(app, DEBUG)
JWTManager(app)

blueprint = Blueprint('api', __name__)
api = Api(blueprint, version = '1.0.0', title = 'PetWalk Notifier API')

socketio = Websocket(app)


from .endpoints.emit import api as http


api.add_namespace(http)

app.register_blueprint(blueprint)
