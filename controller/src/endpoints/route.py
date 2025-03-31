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
    'declared_distance': fields.Integer(description="Declared distance of the route in meters", example=1000),
    'is_prefer_green': fields.Boolean(description="Whether user prefers green areas", example=False),
    'is_avoid_green': fields.Boolean(description="Whether user would like to avoid green areas", example=False),
    'is_include_wheather': fields.Boolean(description="Whether route should be fitted to current wheather", example=False),
})

route_model = api.model('Route', {
    'id': fields.String(description="Unique ID of the route", example="6752269f6f218f859668c4ba"),
    'declared_parameters': fields.Nested(declared_parameters_model),
    'real_distance': fields.Integer(description="Real calculated distance of the route in meters", example=1000),
    'timestamp': fields.String(description="Timestamp of the route generation", example="2024-12-05 21:18:07"),
})

route_list_model = api.model('RoutesList', {
    'routes': fields.List(fields.Nested(route_model), description="List of routes")
})


@api.route('/')
class Route(Resource):
    @api.doc(
        params={
            "user_id": {"description": "Filter routes by user ID.", "example": "671f880f5bf26ed4c9f540fd", "required": False},
        }
    )
    @api.response(200, "OK")
    @api.response(500, "Internal Server Error")
    @api.marshal_with(route_list_model, code=200)
    def get(self):
        """
        Fetch routes based on user_id
        """
        pass

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
