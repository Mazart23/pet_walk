import logging
import os
from datetime import datetime

from flask import request
from flask_restx import Resource, fields, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

from ..database.queries import Queries as db
from ..utils.request import send_request
from ..utils.apps import Services
from ..utils.apps import Url


log = logging.getLogger('POST')

api = Namespace('post')

reaction_model = api.model('Reaction', {
    'id': fields.String(description="Unique ID of the reaction", example="12345"),
    'user_id': fields.String(description="ID of the user who reacted", example="671f880f5bf26ed4c9f540fd"),
    'reaction_type': fields.String(description="Type of reaction", example="heart")
})

post_model = api.model('Post', {
    'id': fields.String(description="Unique ID of the post", example="6752269f6f218f859668c4ba"),
    'content': fields.String(description="Content of the post", example=":p"),
    'images': fields.List(fields.String, description="List of image URLs", example=["https://i.imgur.com/IszRpNP.jpeg", "https://i.imgur.com/mGjZUFQ.jpeg"]),
    'user': fields.Nested(api.model('User', {
        'id': fields.String(description="User ID of the post creator", example="671f880f5bf26ed4c9f540fd"),
        'username': fields.String(description="Username of the post creator", example="Julia"),
        'image': fields.String(description="Profile image URL of the post creator", example="https://i.imgur.com/9P3c7an.jpeg")
    }), description="User information of the post creator"),
    'location': fields.String(description="Location of the post", example="Krakow"),
    'timestamp': fields.String(description="Timestamp of the post", example="2024-12-05 21:18:07"),
    'reactions': fields.List(fields.Nested(reaction_model), description="List of reactions to the post")
})



post_list_model = api.model('PostList', {
    'posts': fields.List(fields.Nested(post_model), description="List of posts")
})


@api.route('/')
class Post(Resource):
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
    @api.marshal_with(post_model, code=201)
    @api.response(201, "Post created successfully")
    @api.response(400, "Invalid data provided")
    @api.response(500, "Failed to create post")
    def put(self):
        """
        Create a new post
        """
        user_id = get_jwt_identity()
        queries = db()  

        try:
            # Parse form data
            content = request.form.get('content')
            location = request.form.get('location')
            files = request.files.getlist('images')

            # Validate required fields
            if not content:
                return {"message": "'content' is a required field."}, 400

            # Validate user existence
            user = queries.get_user_by_id(user_id)
            if not user:
                return {"message": "User not found"}, 404

            # Upload files to Imgur
            image_urls = []
            if files:
                headers = {"Authorization": f"Client-ID {os.environ.get('IMGUR_CLIENT_ID')}"}

                for file in files:
                    try:
                        response = send_request('POST', Url.IMGUR, files={'image': file}, headers=headers)

                        if response.status_code != 200:
                            log.error(f"Failed to upload image to Imgur: {response}")
                            return {"message": "Failed to upload one or more images to Imgur."}, 500

                        imgur_data = response.json()
                        image_urls.append(imgur_data['data']['link'])

                    except Exception as e:
                        log.error(f"Exception during file upload to Imgur: {e}")
                        return {"message": "Failed to upload images to Imgur."}, 500

            # Prepare post data
            post_data = {
                "description": content,   
                "images_urls": image_urls,
                "comments": [],
                "timestamp": datetime.utcnow(),
                "location": location,
                "reactions": [],
                "user_id": ObjectId(user_id),  
            }

            # Insert post into the database
            post_id = queries.create_post(post_data)
            if not post_id:
                return {"message": "Failed to create post."}, 500

            log.info(f"Post created successfully with ID: {post_id}")
            return {
                "id": str(post_id),
                "content": content,
                "images": image_urls,
                "user": {
                    "id": user_id,
                    "username": user.get("username"),
                    "image": user.get("image"),
                },
                "location": location,
                "timestamp": datetime.utcnow().isoformat(),
                "reactions": [],
            }, 201

        except Exception as e:
            log.error(f"Error in PUT /posts: {e}")
            return {"message": "An unexpected error occurred."}, 500

    def patch(self):
        '''
        edit
        '''

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
        

@api.route('/search')
class Search(Resource):
    search_model = api.model(
        'Search model',
        {
            'username': fields.String(description="Partial or full username", example="Fra"),
            'content': fields.String(description="Search content", example="bio text or other"),
        }
    )

    @api.doc(params={
        'query': {'description': 'Search query string (username or content)', 'example': 'Fra', 'required': True},
        'type': {'description': 'Search type: username or content', 'example': 'username', 'required': True},
    })
    @api.response(200, 'OK')
    @api.response(400, 'Bad Request')
    @api.response(404, 'No results found')
    @api.response(500, 'Internal Server Error')
    def get(self):
        """
        Search for users by username or content.
        """
        try:
            query = request.args.get('query')
            search_type = request.args.get('type')

            if not query or not search_type:
                log.error("Missing required query or type parameters.")
                return {"message": "Bad Request: query and type are required parameters."}, 400

            log.info(f"Search request received with query: {query}, type: {search_type}")

            queries = db()

            if search_type.lower() == 'username':
                results = queries.search_users_by_username(query) or []
                if not results:
                    log.info(f"No results found for username: {query}")
                    return {"message": "No results found for username."}, 404
                log.info(f"Found {len(results)} users for query: {query}")
                return {"users": results}, 200

            elif search_type.lower() == 'content':
                results = queries.search_posts(search_term=query) or []
                if not results:
                    log.info(f"No results found for content: {query}")
                    return {"message": "No results found for content."}, 404

                log.info(f"Found {len(results)} posts for query: {query}")
                return {"posts": results}, 200

            else:
                log.error(f"Invalid search type: {search_type}")
                return {"message": "Bad Request: type must be 'username' or 'content'."}, 400

        except Exception as e:
            log.error(f"Error in GET /search: {e}")
            api.abort(500, "An unexpected error occurred while processing your request.")

