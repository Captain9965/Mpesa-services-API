from src import create_app,db
from flask.cli import FlaskGroup
import os


new_app = create_app()
cli = FlaskGroup(new_app)
new_app.route("/")
def home():
    return "<body>Welcome!</body>"


#create a new command called "create_db"
@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    
if __name__ == "__main__":
    os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'
    cli()
    