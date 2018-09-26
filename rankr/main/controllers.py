from flask import current_app, jsonify, Blueprint
from rankr.analyzer import Analyzer
from rankr.dbconnector import db


main = Blueprint('main', __name__)

@main.route('/')
def index():
	a = Analyzer(current_app.config["LEAGUE_ID"])
	return jsonify(a.get_weekly_ranking_errors(2))
