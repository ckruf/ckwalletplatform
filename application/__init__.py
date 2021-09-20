from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()

def create_app():
    """Construct the core application"""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    api = Api(app=app, version='1.0', title='CKplatform', description='A simple wallet platform to respond to Wegas requests')
    db.init_app(app)
    migrate = Migrate(app, db)
    from application import models

    from .routes import wallet_ns
    api.add_namespace(wallet_ns)

    return app