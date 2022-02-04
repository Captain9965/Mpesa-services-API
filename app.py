from src import create_app
import os

new_app = create_app()
new_app.route("/")
def home():
    return "<body>Welcome!</body>"

if __name__ == "__main__":
    os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'
    new_app.run(host= "0.0.0")