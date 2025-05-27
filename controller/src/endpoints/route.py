import logging
import json
from datetime import datetime

from flask import request
from flask_restx import Resource, fields, Namespace
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required

from ..database.queries import Queries as db
from ..utils.request import send_request
from ..utils.apps import Services
from ..utils.algorithm import algorithm
from ..utils.weather import get_weather_info

log = logging.getLogger('ROUTE')

api = Namespace('route')

point_model = api.model('RoutePointModel', {
    'latitude': fields.Float(description="Latitude coordinate"),
    'longitude': fields.Float(description="Longitude coordinate")
})

declared_parameters_model = api.model('DeclaredPameters', {
    'point': fields.Nested(point_model),
    'declared_distance': fields.Integer(description="Declared distance of the route in meters", example=1000),
    'is_prefer_green': fields.Boolean(description="Whether user prefers green areas", example=False),
    'is_avoid_green': fields.Boolean(description="Whether user would like to avoid green areas", example=False),
    'is_include_weather': fields.Boolean(description="Whether route should be fitted to current wheather", example=False),
})

route_obj_model = api.model('RouteObj', {
    'type': fields.String(description="Type of the route", example="LineString"),
    'coordinates': fields.List(fields.List(fields.Float), description="List of coordinates forming the route"),
})

route_model = api.model('Route', {
    'id': fields.Integer(description="Unique ID of the route", example=1),
    'route': fields.Nested(route_obj_model),
    'declared_parameters': fields.Nested(declared_parameters_model),
    'real_distance': fields.Integer(description="Real calculated distance of the route in meters", example=1000),
    'timestamp': fields.String(description="Timestamp of the route generation", example="2024-12-05 21:18:07"),
})

route_list_model = api.model('RoutesList', {
    'routes': fields.List(fields.Nested(route_model), description="List of routes")
})

delete_route_model = api.model('DeleteRoute', {
    'id': fields.Integer(description="Unique ID of the route", example=1),
})


@api.route('/')
class Route(Resource):
    @api.doc(params={
        'Authorization': {
            'description': 'Bearer token for authentication',
            'required': True,
            'in': 'header',
            'default': 'Bearer '
        }
    })
    @api.response(200, "OK")
    @api.response(500, "Internal Server Error")
    @api.marshal_with(route_list_model, code=200)
    @jwt_required()
    def get(self):
        """
        Fetch routes based on user_id
        """
        user_id = get_jwt_identity()

        queries = db()

        data = queries.get_routes_by_user_id(user_id)

        for dct in data:
            p_coords = json.loads(dct.pop('point'))['coordinates']
            dct['declared_parameters'] = {
                'point': {'latitude': p_coords[1], 'longitude': p_coords[0]},
                'declared_distance': dct.pop('declared_distance'),
                'is_avoid_green': dct.pop('is_avoid_green'),
                'is_prefer_green': dct.pop('is_prefer_green'),
                'is_include_weather': dct.pop('is_include_weather'),
            }
            dct['route'] = json.loads(dct.pop('route'))

        return {'routes': data}
    
    @api.doc(params={
        'Authorization': {
            'description': 'Bearer token for authentication',
            'required': True,
            'in': 'header',
            'default': 'Bearer '
        }
    })
    @api.expect(delete_route_model, validate=True)
    @api.response(200, "OK")
    @api.response(500, "Internal Server Error")
    @jwt_required()
    def delete(self):
        """
        Delete route based on id of the route
        """
        user_id = get_jwt_identity()
        route_id = request.json.get('id')

        queries = db()

        status = queries.delete_route(route_id, user_id)

        if not status:
            api.abort(500)
        
        return 'OK', 200
    
    @api.doc(params={
        'Authorization': {
            'description': 'Bearer token for authentication',
            'required': False,
            'in': 'header',
            'default': 'Bearer '
        }
    })
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

        point = json.get('point', {})
        latitude = point.get('latitude', 0.0)
        longitude = point.get('longitude', 0.0)
        declared_distance = json.get('declared_distance', 1000)
        is_prefer_green = json.get('is_prefer_green', False)
        is_avoid_green = json.get('is_avoid_green', False)
        is_include_weather = json.get('is_include_weather', False)

        weather_conditions = {}
        if is_include_weather:
            try:
                weather_conditions = get_weather_info(latitude, longitude)
                log.info(f"Weather conditions at ({latitude}, {longitude}): {weather_conditions}")
            except Exception as e:
                log.error(f"WeatherAPI error: {str(e)}")
                weather_conditions = {
                    "rain_past_6h": False,
                    "rain_next_2h": False
                }

        coords, real_distance = algorithm(
            (latitude, longitude), 
            declared_distance, 
            is_prefer_green, 
            is_avoid_green, 
            is_include_weather
        )

        if not coords:
            api.abort(500)

        route_id = ''
        timestamp = ''
        user_id = None

        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except:
            pass
        
        if user_id:
            queries = db()

            route_data = {
                "route": coords,
                "latitude": latitude,
                "longitude": longitude,
                "real_distance": real_distance,
                "declared_distance": declared_distance,
                "is_prefer_green": is_prefer_green,
                "is_avoid_green": is_avoid_green,
                "is_include_weather": is_include_weather,
                "user_id": user_id
            }

            result = queries.insert_route(route_data)

            if not result:
                api.abort(500)
                
            route_id = result['id']
            timestamp = result['timestamp']
        
        else:
            route_id = -1
            timestamp = datetime.now()
        
        output_json = {
            "id": route_id,
            "route": {
                'type': 'LineString',
                'coordinates': coords,
            },   
            "real_distance": real_distance,
            "declared_parameters": {
                "point": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "declared_distance": declared_distance,
                "is_prefer_green": is_prefer_green,
                "is_avoid_green": is_avoid_green,
                "is_include_weather": is_include_weather,
            },
            "timestamp": timestamp
        }
        return output_json, 200