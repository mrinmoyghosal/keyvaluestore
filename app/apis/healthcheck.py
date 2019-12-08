from flask_restplus import Namespace, Resource

api = Namespace(
    name='healthcheck',
    description='Health Information for the service.',
    path='/',
)


@api.route('')
@api.hide
class HealthCheck(Resource):

    @api.response(204, 'Success.')
    def get(self):
        """
        Returns the health status of the service.
        """
        return None, 204
