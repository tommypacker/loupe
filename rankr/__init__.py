from flask import Flask
from config import config

def create_app():
	app = Flask(__name__)
	app.config["DEBUG"] = config["debug"]
	app.config["LEAGUE_ID"] = config["league_id"]
	return app

app = create_app()

from rankr import routes
