import rankr.constants as constants

from flask import current_app, jsonify, Blueprint
from rankr.analyzer import Analyzer
from rankr.dbconnector import MongoConnector


main = Blueprint('main', __name__)
rankrDB = MongoConnector()

#TODO: Add input validation

@main.route('/')
def index():
	return "Rankr"	

@main.route('/stats/<int:week>/')
def all_stats(week):
	a = Analyzer(current_app.config["LEAGUE_ID"], rankrDB)
	res = a.get_all_analyst_errors(week)
	return jsonify(res)

@main.route('/stats/<int:week>/<int:position>/')
def position_stats(week, position):
	a = Analyzer(current_app.config["LEAGUE_ID"], rankrDB)
	res = a.get_all_analyst_errors(week)
	position = constants.POSITION_MAP[position]
	return jsonify(res[position])

@main.route('/stats/aggregated/<int:week>/')
def aggregated_stats(week):
	a = Analyzer(current_app.config["LEAGUE_ID"], rankrDB)
	res = a.get_aggregated_analyst_errors(week)
	return jsonify(res)

@main.route('/stats/aggregated/season/')
def aggregated_season_stats():
	return "Season"
