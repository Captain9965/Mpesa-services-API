from decouple import config

class DefaultConfig():
    TUNNEL_CONNECTION = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = config("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(DefaultConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = config("DATABASE_URL")

class ProductionConfig(DefaultConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = config("PROD_DATABASE_URL")