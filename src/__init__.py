from flask import Flask, session
from decouple import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#initialize the database:
db = SQLAlchemy()
migrate = Migrate()
#import the database models:
from .models import (
    StkRequestDump,
    ResponseDump
)
from .stkPush import stkBp

def create_app():
    app = Flask(__name__)
    print(__name__)
    #configure the application:
    app.config.from_object(config("APP_CONFIG"))
    #register blueprints:
    app.register_blueprint(stkBp)
    with app.app_context():
        #callback to initialize the application:
        db.init_app(app)
        #database migrations:
        migrate.init_app(app, db)
        #create all tables:
        db.create_all()
    return app