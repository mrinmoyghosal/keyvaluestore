import os
import time

from importlib import import_module
from logging import Filter, getLogger

from flask import Blueprint, Flask
from flask_apscheduler import APScheduler
from flask_restplus import Api
from flask_redis import FlaskRedis
from fakeredis import FakeRedis
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask_prometheus_metrics import register_metrics

from app.config import BaseConfig
from app.apis.healthcheck import api as healthcheck_api
from app.apis.keyvaluestore import api as keyvaluestore_api

scheduler = APScheduler()


def create_dispatcher(app) -> DispatcherMiddleware:
    """
    App factory for dispatcher middleware managing multiple WSGI apps
    """
    return DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})


class HealthLogFilter(Filter):
    def filter(self, log_record):
        return 'GET /health' not in log_record.msg


@scheduler.task('interval', id='clean_expired_keys', seconds=1)
def clean_expired_keys():
    all_keys = redis_store.hgetall('expiry_keys')
    for key in all_keys:
        val = redis_store.hget('expiry_keys', key)
        if float(val.decode()) < time.time():
            redis_store.hdel('store', key)
            redis_store.hdel('expiry_keys', key)
            print(f'Expired Key deleted {key}')


def create_config(fully_qualified_config_name: str) -> object:
    """ Creates a flask compatible config from a string describing the "path" to the definition.

    The `fully_qualified_config_name` will usually be something like
    'app.config.ProductionConfig' or 'app.config.DevelopmentConfig'.

    :param fully_qualified_config_name: The "path" to the definition of the config to be created.
    :type fully_qualified_config_name: str
    :return: The config object, usable by a flask app
    :rtype: object
    """

    *module_names, class_name = fully_qualified_config_name.split('.')
    module_name = '.'.join(module_names)
    try:
        module = import_module(module_name)
        klass = getattr(module, class_name)
        return klass()

    except (AttributeError, TypeError, ValueError, ModuleNotFoundError) as e:
        raise ValueError(f'The config "{fully_qualified_config_name}" is invalid: {str(e)}')


def create_app(config: BaseConfig) -> Flask:
    """
    Creates and returns a Flask application object configured

    :param config: A config object usable by Flask's 'app.config.from_object()' function.
    :type config: object
    :return: The Flask application object
    :rtype: Flask
    """
    app = Flask(config.SERVICE_NAME)
    app.config.from_object(config)

    # Configure Redis client
    if app.testing:
        redis_store = FlaskRedis.from_custom_provider(FakeRedis())
    else:
        redis_store = FlaskRedis()
    redis_store.init_app(app)
    app.redis = redis_store

    logger = getLogger("werkzeug")
    logger.addFilter(HealthLogFilter())

    api_blueprint = Blueprint(config.SERVICE_NAME, __name__)
    health_blueprint = Blueprint("healthcheck", __name__)

    api = Api(
        api_blueprint,
        title=f"{config.SERVICE_LONG_NAME} API",
        version=f"{config.API_VERSION}",
        description=config.SERVICE_DESCRIPTION,
    )

    # Add Keyvalue store api namespace
    api.add_namespace(keyvaluestore_api, path="")

    # Add endpoints for prometheus_client
    register_metrics(app, app_version="0.0.1", app_config="production")

    healthcheck = Api(
        health_blueprint,
        title="Healthcheck Endpoint",
        version="1",
        description=f"An API returning health information for the {config.SERVICE_NAME} service.",
    )
    healthcheck.add_namespace(healthcheck_api, path="")

    app.register_blueprint(api_blueprint, url_prefix="/api")
    app.register_blueprint(health_blueprint, url_prefix="/health")

    return app, redis_store


app_settings = os.environ.get("APP_SETTINGS", "app.config.ProductionConfig")
config = create_config(app_settings)
app, redis_store = create_app(config)
scheduler.init_app(app)
scheduler.start()


if __name__ == "__main__":
    run_simple(
        "0.0.0.0",
        5000,
        create_dispatcher(app),
        use_reloader=True,
        use_debugger=True,
        use_evalex=True,
    )
