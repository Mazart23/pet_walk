import logging
from threading import Lock

from flask import Flask, request
from flask_socketio import SocketIO, join_room
from flask_jwt_extended import decode_token

from .singleton import SingletonMeta
from .apps import Services


log = logging.getLogger('WEBSOCKET')


class Websocket(metaclass=SingletonMeta):

    def __init__(self, app: Flask | None):
        '''
        app - running flask application
        connected_users - states of users: True - connected, False - disconnected
        '''
        service = Services.CLIENT
        self.app = SocketIO(app, cors_allowed_origins=f'{service.http}://{service.ip_host}:{service.port}', logger=True, engineio_logger=True)

        self.connected_users = {}
        self.users_lock = Lock()

        @self.app.on('connect')
        def on_connect():
            self.handle_connect()

        @self.app.on('disconnect')
        def on_disconnect():
            self.handle_disconnect()
    
    def handle_connect(self) -> None:
        token = request.args.get('token')
        decoded_token = decode_token(token, csrf_value=None, allow_expired=False)

        user_id = decoded_token["sub"]

        if user_id:
            with self.users_lock:
                self.connected_users[user_id] = True
            join_room(user_id)
            log.info(f'User connected with {user_id = }.')

    def handle_disconnect(self) -> None:
        token = request.args.get('token')
        decoded_token = decode_token(token, csrf_value=None, allow_expired=True)

        user_id = decoded_token["sub"]

        if user_id:
            with self.users_lock:
                self.connected_users[user_id] = False
            log.info(f'User disconnected with {user_id = }.')

    def is_connected(self, user_id) -> bool:
        with self.users_lock:
            result = self.connected_users.get(user_id, False)
        return result

    def emit(self, *args, **kwargs) -> None:
        self.app.emit(*args, **kwargs)
