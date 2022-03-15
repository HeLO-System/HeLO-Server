# HeLO.py
import json, os, logging
from flask import Flask, render_template, jsonify
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_jwt_extended import JWTManager
from rest._routes import initialize_routes
from database._db import initialize_db


# init components
logging.basicConfig(encoding='utf-8', level=logging.INFO, format=f"%(filename)20s:%(lineno)-3s - %(funcName)-30s %(message)s")

app = Flask(__name__)

DB = { 
    'USERNAME': os.environ.get('DB_USERNAME'),
    'PASSWORD': os.environ.get('DB_PASSWORD'),
    'HOST': os.environ.get('DB_HOST'),
    'NAME': os.environ.get('DB_NAME')
}
app.config['MONGODB_HOST'] = ('mongodb+srv://%(USERNAME)s:%(PASSWORD)s@%(HOST)s/%(NAME)s') % DB
initialize_db(app)
initialize_routes(Api(app))

bcrypt = Bcrypt(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
jwt = JWTManager(app)

# needs to be true for custom error messages
app.config["PROPAGATE_EXCEPTIONS"] = True

# custom error message for wrong JWTs
@jwt.invalid_token_loader
def invalid_token_callback(s):
    return jsonify("Wrong Token or no Admin"), 401


# home page: offer some explanation how to use the API
@app.route('/')
def home():
    return render_template('home.html', apis = json.loads(open('static/apis.json', 'r').read())), 200


# start app
if __name__ == "__main__":
    app.run()

