import logging
from datetime import datetime

from flask import request
from flask_restx import Resource, fields, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..database.queries import Queries as db
from ..utils.request import send_request
from ..utils.apps import Services
from ..utils.algorithm import algorithm


log = logging.getLogger('ROUTE')

api = Namespace('route')

declared_parameters_model = api.model('DeclaredPameters', {
    'declared_distance': fields.Int(description="Declared distance of the route in meters", example=1000),
    'is_prefer_green': fields.Boolean(description="Whether user prefers green areas", example=False),
    'is_avoid_green': fields.Boolean(description="Whether user would like to avoid green areas", example=False),
    'is_include_wheather': fields.Boolean(description="Whether route should be fitted to current wheather", example=False),
})

route_model = api.model('Route', {
    'id': fields.String(description="Unique ID of the route", example="6752269f6f218f859668c4ba"),
    'declared_parameters': fields.Nested(declared_parameters_model),
    'real_distance': fields.Int(description="Real calculated distance of the route in meters", example=1000),
    'timestamp': fields.String(description="Timestamp of the route generation", example="2024-12-05 21:18:07"),
})

route_list_model = api.model('RoutesList', {
    'routes': fields.List(fields.Nested(route_model), description="List of routes")
})


@api.route('/')
class Route(Resource):
    @api.doc(
        params={
            "user_id": {"description": "Filter posts by user ID.", "example": "671f880f5bf26ed4c9f540fd", "required": False},
            "last_timestamp": {"description": "Timestamp of the last fetched post (ISO format)", "example": "2025-01-01T12:00:00", "required": False},
            "limit": {"description": "Number of posts to fetch", "example": 10, "required": False}
        }
    )
    @api.response(200, "OK")
    @api.response(500, "Failed to fetch posts")
    @api.marshal_with(post_list_model, code=200)
    def get(self):
        """
        Fetch posts based on optional filters (e.g., user ID, timestamp, pagination)
        """
        try:
            # Read query parameters
            user_id = request.args.get('user_id')
            last_timestamp = request.args.get('last_timestamp')
            limit = int(request.args.get('limit', 10))

            # Initialize query
            query = {}
            if user_id:
                try:
                    query['user_id'] = ObjectId(user_id)
                except Exception:
                    log.error(f"Invalid user_id format: {user_id}")
                    return {"message": "Invalid user_id format."}, 400

            if last_timestamp:
                try:
                    query['timestamp'] = {'$lt': datetime.fromisoformat(last_timestamp)}
                except ValueError:
                    log.error(f"Invalid timestamp format: {last_timestamp}")
                    return {"message": "Invalid timestamp format. Use ISO format."}, 400

            log.info(f"Fetching posts with query: {query}, limit: {limit}")

            # Fetch posts with aggregation pipeline
            posts = db().fetch_posts(query=query, limit=limit)

            log.info(f"Posts fetched: {posts}")
            return {"posts": posts}, 200

        except Exception as e:
            log.error(f"Error in GET /posts: {e}")
            return {"message": "Failed to fetch posts"}, 500


    @jwt_required()
    @api.expect(declared_parameters_model, validate=True)
    @api.marshal_with(route_model, code=200)
    @api.response(200, 'OK')
    @api.response(400, "Bad Request")
    @api.response(404, "Not found")
    @api.response(500, "Internal Server Error")
    def post(self):
        """
        Generate a new route based on parameters
        """
        json = request.json
        user_id = get_jwt_identity()

        queries = db()

        point = json.get('point')
        latitude = point.get('latitude')
        longitude = point.get('longitude')
        declared_distance = json.get('declared_distance')
        is_prefer_green = json.get('is_prefer_green')
        is_avoid_green = json.get('is_avoid_green')
        is_include_wheather = json.get('is_include_wheather')

        route, real_distance = algorithm((latitude, longitude), declared_distance, is_prefer_green, is_avoid_green, is_include_wheather)

        if not route:
            api.abort(500)

        route_data = {
            "route": route,   
            "real_distance": real_distance,
            "declared_distance": declared_distance,
            "is_prefer_green": is_prefer_green,
            "is_avoid_green": is_avoid_green,
            "is_include_wheather": is_include_wheather,
            "user_id": user_id
        }

        route_id, timestamp = queries.insert_route(route_data)
        if not route_id:
            api.abort(500)

        output_json = {
            "id": route_id,
            "route": route,   
            "real_distance": real_distance,
            "declared_parameters": {
                "point": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "declared_distance": declared_distance,
                "is_prefer_green": is_prefer_green,
                "is_avoid_green": is_avoid_green,
                "is_include_wheather": is_include_wheather,
            },
            "timestamp": timestamp
        }
        return output_json, 200

    @jwt_required()
    @api.response(200, "Post deleted successfully")
    @api.response(404, "Post not found")
    @api.response(403, "Unauthorized to delete this post")
    @api.response(500, "Failed to delete post")
    def delete(self):
        """
        Delete a post along with its associated comments and reactions
        """
        user_id = get_jwt_identity()  # Get the ID of the logged-in user
        queries = db()  # Database queries instance

        try:
            post_id = request.json.get('id')
            if not post_id:
                return {"message": "'id' is a required query parameter."}, 400

            post_deleted = queries.delete_post(post_id, user_id)
            if not post_deleted:
                return {"message": "Failed to delete the post."}, 500

            log.info(f"Post with ID {post_id} deleted successfully.")
            return {"message": "Post deleted successfully."}, 200

        except Exception as e:
            log.error(f"Error in DELETE /posts: {e}")
            return {"message": "An unexpected error occurred."}, 500


@api.route('/single')
class SinglePost(Resource):
    @api.doc(
        params={
            "id": {"description": "Unique ID of the post.", "example": "671f880f5bf26ed4c9f540fd", "required": True},
            'Authorization': {
                'description': 'Bearer token for authentication',
                'required': True,
                'in': 'header',
                'default': 'Bearer '
            }
        }
    )
    @api.response(200, "OK")
    @api.response(500, "Internal Server Error")
    @api.marshal_with(post_model, code=200)
    def get(self):
        """
        Fetch single post based on its ID
        """
        try:
            post_id = request.args.get('id')
            
            post = db().fetch_posts(query={'_id': ObjectId(post_id)}, limit=1)

            assert post

            log.info(f"Post fetched: {post}")
            return post[0], 200

        except Exception as e:
            log.error(f"Error: {e}")
            return {"message": "Failed to fetch post"}, 500
