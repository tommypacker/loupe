from flask import current_app, jsonify, render_template

from loupe import app
from loupe.analyzer import Analyzer
from loupe.db import MongoConnector

loupeDB = MongoConnector().db

@app.route('/')
def home():
	a = Analyzer(current_app.config["LEAGUE_ID"], loupeDB)
	return render_template('index.html', latest_week=a.get_latest_week())

@app.route('/stats/<int:week>/')
def weekly_individual_stats(week):
	a = Analyzer(current_app.config["LEAGUE_ID"], loupeDB)
	res = a.get_weekly_individual_errors(week)
	return jsonify(res)

@app.route('/stats/season/')
def season_individual_stats():
	a = Analyzer(current_app.config["LEAGUE_ID"], loupeDB)
	res = a.get_season_individual_errors()
	return jsonify(res)

@app.route('/stats/sum/<int:week>/')
def weekly_summed_stats(week):
	a = Analyzer(current_app.config["LEAGUE_ID"], loupeDB)
	res = a.get_weekly_summed_errors(week)
	return jsonify(res)

@app.route('/stats/sum/season/')
def season_summed_stats():
	a = Analyzer(current_app.config["LEAGUE_ID"], loupeDB)
	res = a.get_season_summed_errors()
	return jsonify(res)
