from flask_restx import fields, marshal
from werkzeug.exceptions import BadRequest


class DynamicModelField(fields.Raw):
    def __init__(self, models, *args, **kwargs):
        """
        models: dict - a dictionary of models that will be used based on the value of 'notification_type'
        """
        self.models = models
        super().__init__(*args, **kwargs)
    
    def format(self, value):
        """
        Format the value based on 'notification_type' and use the correct model
        """
        if 'reaction_type' in value:
            notification_type = 'reaction'
        elif 'city' in value:
            notification_type = 'scan'
        elif 'post_id' in value:
            notification_type = 'comment'
        else:
            raise BadRequest('Invalid data')

        model = self.models.get(notification_type)

        return marshal(value, model)
    
    def __call__(self, value, **kwargs):
        '''
        This is where we validate and format the field based on the notification type
        '''
        return self.format(value)
