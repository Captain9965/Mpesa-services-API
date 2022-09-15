from src import create_app
from flask.cli import FlaskGroup
import os


new_app = create_app()
cli = FlaskGroup(new_app)
new_app.route("/")
def home():
    return "<body>Welcome!</body>"

if __name__ == "__main__":
    os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'
    cli()
    