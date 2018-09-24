from flask import Flask
from rankr.main.controllers import main


def create_app(config):
	app = Flask(__name__)
	app.config["DEBUG"] = config["debug"]
	app.config["LEAGUE_ID"] = config["league_id"]
	app.register_blueprint(main, url_prefix='/')
	return app