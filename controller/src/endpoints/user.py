import logging
import os

import bcrypt
from flask import request
from flask_restx import Resource, fields, Namespace
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

from ..database.queries import Queries as db
from ..utils.request import send_request


log = logging.getLogger('USER')

api = Namespace('user')


status_model = api.model(
    'Status model',
    {
        'status': fields.String(),
    }
)

user_model = api.model(
    'User model', 
    {
        'id': fields.String(description="ID of the user", example="1234"),
        'username': fields.String(description="Username of the user", example="Julia"),
        'bio': fields.String(description="Bio of the user", example="bio"),
        'email': fields.String(description="Email address of the user", example="kasia@gmail.com"),
        'profile_picture_url': fields.String(description="Profile picture URL", example="https://i.imgur.com/9P3c7an.jpeg"),
        'posts': fields.List(fields.String, description="List of user posts IDs", example=["67524226995227baafe49eed"]),
        'location': fields.String(description="User location (city)", example="Krakow"),
        'is_premium': fields.Boolean(description="Whether user has premium status", example=True),
        'is_private': fields.Boolean(description="Whether user's profile is private", example=False),
        'phone': fields.String(description="Phone number of the user", example="123456789"),
    }
)

login_input_model = api.model(
    'Login input model',
    {
        'username': fields.String(),
        'password': fields.String(),
    }
)

signup_input_model = api.model(
    'Signup input model',
    {
        'username': fields.String(required=True),
        'email': fields.String(required=True),
        'password': fields.String(required=True),
        'phone': fields.String(required=False),
    }
)


login_output_model = api.model(
    'Login output model',
    {
        'access_token': fields.String()
    }
)

edit_password_model = api.model(
    'Edit password model',
    {
        'username': fields.String(),
        'current_password': fields.String(),
        'new_password': fields.String(),
    }
)

user_profile_picture_model = api.model(
    'User profile picture model',
    {
        'profile_picture_url': fields.String(),
    }
)


@api.route('/')
class User(Resource):
    @api.doc(params={'username': {'description': 'Unique username', 'example': 'Julia', 'required': True}})
    @api.marshal_with(user_model, code=200)
    @api.response(200, 'OK')
    @api.response(400, 'Bad Request')
    @api.response(404, 'Not Found')
    def get(self):
        '''
        Fetch user data
        '''
        username = request.args.get('username')
        if not username:
            api.abort(400, 'Bad Request')

        queries = db()

        user_data = queries.get_user_by_username(username)
        log.info(f"User data fetched: {user_data}")

        if not user_data:
            log.error(f'Error fetching data for {username}')
            api.abort(404, "User Not Found")
        
        return user_data, 200


@api.route('/self')
class Self(Resource):
    @api.marshal_with(user_model, code=200)
    @api.response(200, 'OK')
    @api.response(400, 'Bad Request')
    @api.response(401, 'Unauthorized')
    @jwt_required()
    def get(self):
        '''
        Fetch self user data
        '''
        user_id = get_jwt_identity()

        queries = db()

        user_data = queries.get_user_by_id(user_id)

        if not user_data:
            log.error(f'Error fetching data for {user_id}')
            api.abort(404, "User Not Found")
        
        user_data['id'] = user_id

        return user_data, 200
    
    @api.response(200, 'OK')
    @api.response(400, 'Bad Request')
    @api.response(401, 'Unauthorized')
    @jwt_required()
    def put(self):
        '''
        Update self user data
        '''
        user_id = get_jwt_identity()
        data = request.get_json()

        queries = db()

        valid_fields = {
            'bio', 'email', 'location',
            'is_private', 'phone'
        }
        if not all(field in valid_fields for field in data.keys()):
            return {"message": "Invalid fields in request"}, 400

        updated = queries.update_user_by_id(user_id, data)

        if not updated:
            log.error(f'Error updating data for {user_id}')
            api.abort(400, "Update Failed")

        return {"message": "User data updated successfully"}, 200


@api.route('/login')
class Login(Resource):
    @api.expect(login_input_model, validate=True)
    @api.marshal_with(login_output_model, code=200)
    @api.response(200, 'OK')
    @api.response(400, 'Bad Request')
    @api.response(401, 'Unauthorized')
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        queries = db()

        user = queries.get_user_password_by_username(username)

        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.get('password').encode('utf-8')):
            api.abort(401, 'Unauthorized')
        
        access_token = create_access_token(identity=str(user.get('id')))
        return {'access_token': access_token}, 200
    
@api.route('/signup')
class Signup(Resource):
    @api.expect(signup_input_model, validate=True)
    @api.response(200, 'User created successfully')
    @api.response(400, 'Bad Request')
    @api.response(500, 'Internal Server Error')
    def post(self):
        """Sign up a new user"""
        try:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            phone = data.get('phone')

            queries = db()

            if queries.get_user_by_username(username):
                raise BadRequest('Username already exists')

            if queries.get_user_by_email(email):
                raise BadRequest('Email already exists')

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_id = queries.create_user(username, email, hashed_password, phone)

            if user_id is None:
                raise Exception('User not created - empty user_id')

            return {'message': 'User created successfully', 'user_id': str(user_id)}, 200

        except BadRequest as e:
            return {'message': str(e)}, 400
        except Exception as e:
            log.error(f'Error during user creation: {e}')
            return {'message': 'Failed to create user'}, 500

@api.route('/password')
class Password(Resource):
    @api.expect(edit_password_model, validate=True)
    @api.response(200, 'OK')
    @api.response(400, 'Bad Request')
    @api.response(401, 'Unauthorized')
    @api.response(404, 'User not found')
    @api.response(500, 'Internal Server Error')
    @jwt_required()
    def patch(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        
        current_password = data.get('current_password')
        password = data.get('new_password')
        
        queries = db()
        
        user = queries.get_user_by_id(user_id)
        
        if not user:
            api.abort(404, 'User not found')
            
        if not bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
            api.abort(401, 'Unauthorized')
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        queries = db()
        
        result = queries.user_change_password(user_id, hashed_password)
        
        if not result:
            api.abort(500, 'Internal Server Error')
        
        return {}, 200
    