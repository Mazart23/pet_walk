import os
from logging import DEBUG
from datetime import timedelta

from flask import Flask, Blueprint
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from .utils.logger_config import config_logger
from .utils.limiter import configure_limiter
from .utils.cache import configure_cache

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

CORS(app)
config_logger(app, DEBUG)
JWTManager(app)
configure_limiter(app)
configure_cache(app)

blueprint = Blueprint('api', __name__)
api = Api(blueprint, version = '1.0.0', title = 'PetWalk Controller API')


from .endpoints.user import api as user
from .endpoints.config import api as config
from .endpoints.route import api as post


api.add_namespace(user)
api.add_namespace(config)
api.add_namespace(post)

app.register_blueprint(blueprint)
