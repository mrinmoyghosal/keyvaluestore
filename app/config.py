import os


class BaseConfig:
    SERVICE_NAME = "NI Task"
    SERVICE_LONG_NAME = "Redis Key Value Store App"
    SERVICE_DESCRIPTION = "A Simple Flask based service for storing key-value data"
    API_VERSION = "0.0.1"

    REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    SCHEDULER_API_ENABLED = True


class TestConfig(BaseConfig):
    """
    This config is active during testing.
    """
    TESTING = True


class DevelopmentConfig(BaseConfig):
    """
    By default this is the config active in the dev environment deployment.
    """
    DEBUG = True


class ProductionConfig(BaseConfig):
    """By default this is the config active in
    production environment deployments.

    Add here any configuration settings that are (only) relevant for
    the versions deployed in production.
    """
    pass
