from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[]
)


def configure_limiter(app: Flask) -> None:
    limiter.init_app(app)


class LimitFunc:

    @staticmethod
    def limit_logged_users_routes_post() -> None:
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            if user_id:
                return "1 per 15 seconds"
        except:
            pass
        return "1 per 2 minutes"