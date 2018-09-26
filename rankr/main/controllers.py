from flask import current_app, jsonify, Blueprint
from rankr.analyzer import Analyzer
from rankr.dbconnector import MongoConnector


main = Blueprint('main', __name__)
rankrDB = MongoConnector()

@main.route('/')
def index():
	return "Rankr"	

@main.route('/stats/<int:week>/')
def all_stats(week):
	a = Analyzer(current_app.config["LEAGUE_ID"], rankrDB)
	res = a.get_aggregated_analyst_errors(week)
	return jsonify(res)

@main.route('/stats/<int:week>/<int:position>')
def position_stats(week, position):
	return "Errors for week {} position {}".format(week, position)
