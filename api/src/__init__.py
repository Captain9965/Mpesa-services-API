from flask import Flask, session
from decouple import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

#initialize the database:
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
#import the database models:
from .models import (
    StkRequestDump,
    ResponseDump
)
from .stkPush import stkBp
from .reversals import reversalsBp
from .accountBalance import accountBalanceBp

def create_app():
    app = Flask(__name__)
    print(__name__)
    #configure the application:
    app.config.from_object(config("APP_CONFIG"))
    #register blueprints:
    app.register_blueprint(stkBp)
    app.register_blueprint(reversalsBp)
    app.register_blueprint(accountBalanceBp)
    with app.app_context():
        #callback to initialize the application:
        db.init_app(app)
        cors.init_app(app)
        #database migrations:
        migrate.init_app(app, db)
        #create all tables:
        db.create_all()
    return app