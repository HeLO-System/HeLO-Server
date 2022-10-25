# HeLO.py
import json
import logging
import os

from flask import Flask, render_template, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api

from database._db import initialize_db
from discord.auth import initialize_discord_auth
from rest._routes import initialize_routes

# init components
logging.basicConfig(
    encoding="utf-8",
    level=logging.INFO,
    format=f"%(filename)20s:%(lineno)-3s - %(funcName)-30s %(message)s",
)

app = Flask(__name__)

DB = {
    "USERNAME": os.environ.get("DB_USERNAME"),
    "PASSWORD": os.environ.get("DB_PASSWORD"),
    "HOST": os.environ.get("DB_HOST"),
    "NAME_PC": os.environ.get("DB_NAME_PC"),
    "NAME_CONSOLE": os.environ.get("DB_NAME_CONSOLE"),
}
if DB["HOST"] == "localhost":
    app.config["MONGODB_HOST"] = (
        "mongodb://%(USERNAME)s:%(PASSWORD)s@%(HOST)s/%(NAME_PC)s?authSource=admin" % DB
    )
else:
    app.config["MONGODB_SETTINGS"] = [
        {
            "host": "mongodb+srv://%(USERNAME)s:%(PASSWORD)s@%(HOST)s/%(NAME_PC)s" % DB,
            "alias": "default",
        },
        {
            "host": "mongodb+srv://%(USERNAME)s:%(PASSWORD)s@%(HOST)s/%(NAME_CONSOLE)s"
            % DB,
            "alias": "console",
        },
    ]

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["DISCORD_REPORT_MATCH_WEBHOOK"] = os.environ.get(
    "DISCORD_REPORT_MATCH_WEBHOOK"
)
app.config["IS_CONSOLE_API"] = os.environ.get("IS_CONSOLE_API") == "true"
# needs to be true for custom error messagess
app.config["PROPAGATE_EXCEPTIONS"] = True

initialize_db(app)
discord = initialize_discord_auth(app)
initialize_routes(Api(app), discord)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)


# custom error message for wrong JWTs
@jwt.invalid_token_loader
def invalid_token_callback(s):
    return jsonify("Wrong Token or no Admin"), 401


# home page: offer some explanation how to use the API
@app.route("/")
def home():
    return (
        render_template(
            "home.html", apis=json.loads(open("static/apis.json", "r").read())
        ),
        200,
    )


# start app
if __name__ == "__main__":
    app.run()
