from flask import current_app, jsonify, render_template

from rankr import app
from rankr.analyzer import Analyzer
from rankr.db import MongoConnector

rankrDB = MongoConnector().db

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/stats/<int:week>/')
def weekly_individual_stats(week):
	a = Analyzer(current_app.config["LEAGUE_ID"], rankrDB)
	res = a.get_weekly_individual_errors(week)
	return jsonify(res)

@app.route('/stats/season/')
def season_individual_stats():
	a = Analyzer(current_app.config["LEAGUE_ID"], rankrDB)
	res = a.get_season_individual_errors()
	return jsonify(res)

@app.route('/stats/sum/<int:week>/')
def weekly_summed_stats(week):
	a = Analyzer(current_app.config["LEAGUE_ID"], rankrDB)
	res = a.get_weekly_summed_errors(week)
	return jsonify(res)

@app.route('/stats/sum/season/')
def season_summed_stats():
	a = Analyzer(current_app.config["LEAGUE_ID"], rankrDB)
	res = a.get_season_summed_errors()
	return jsonify(res)
