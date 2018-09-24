from flask import current_app, Blueprint
from rankr.analyzer import Analyzer

main = Blueprint('main', __name__)

@main.route('/')
def index():
	a = Analyzer(current_app.config["LEAGUE_ID"])
	return "Welcome to rankr"