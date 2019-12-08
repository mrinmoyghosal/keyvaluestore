import pytest


@pytest.fixture(scope="module")
def test_client():
    from app.main import create_app, create_config
    config = create_config('app.config.TestConfig')
    app, _ = create_app(config)
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()

