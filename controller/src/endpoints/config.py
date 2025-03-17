import logging
import dataclasses

from flask_restx import Resource, fields, Namespace

from ..utils.apps import Service, Services


log = logging.getLogger('CONFIG')

api = Namespace('config')
 

service_model = api.model(
    'Service model',
    {
        'name': fields.String(),
        'http': fields.String(),
        'ip_host': fields.String(),
        'ip': fields.String(),
        'port': fields.String(),
    }
)

services_output_model = api.model(
    'Service output model',
    {
        'services': fields.List(fields.Nested(service_model))
    }
)


@api.route('/services')
class ServicesConfig(Resource):
    @api.marshal_with(services_output_model, code=200)
    @api.response(200, 'OK')
    @api.response(400, 'Bad Request')
    @api.response(500, 'Internal Server Error')
    def get(self):
        service_list = []
        
        try:                    
            for service_name, service_instance in vars(Services).items():
                if isinstance(service_instance, Service):
                    service = {'name': service_name.lower()}
                    
                    for field in dataclasses.fields(Service):
                        field_name = field.name
                        field_value = getattr(service_instance, field_name)
                        service[field_name] = field_value

                    service_list.append(service)
                
        except Exception as e:
            log.error(f'Cannot get services config: {e}')
            api.abort(500, 'Internal Server Error')
        
        return {'services': service_list}, 200
