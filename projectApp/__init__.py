from flask import Flask
from .config import Config

def create_app():
    from . import models, routes, services
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    models.init_app(app)
    routes.init_app(app)
    services.init_app(app)
    return app