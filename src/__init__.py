from flask import Flask
from decouple import config
from .stkPush import stkBp

def create_app():
    app = Flask(__name__)
    print(__name__)
    app.config.from_object(config("APP_CONFIG"))
    app.register_blueprint(stkBp)
    return app