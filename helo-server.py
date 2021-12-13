# HeLO.py
import json, os, logging
from flask import Flask, render_template
from flask_restful import Api
from database._db import initialize_db
from rest._routes import initialize_routes


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


# home page: offer some explanation how to use the API
@app.route('/')
def home():
    return render_template('home.html', apis = json.loads(open('static/apis.json', 'r').read())), 200


# start app
if __name__ == "__main__":
    app.run()

