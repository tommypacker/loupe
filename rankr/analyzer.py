import copy
import json
import operator
import numpy as np
import rankr.constants as constants

from datetime import datetime
from dateutil import rrule
from bson import json_util
from rankr.fetchers.rankings_fetcher import RankingsFetcher
from rankr.fetchers.leaders_fetcher import LeadersFetcher


class Analyzer():
	def __init__(self, league_id, db_connector):
		self._league_id = league_id
		self._rf = RankingsFetcher(self._league_id)
		self._lf = LeadersFetcher(self._league_id)
		self._latest_week = self._find_latest_week()
		self._db = db_connector.db

	def get_all_analyst_errors(self, week):
		return self._get_weekly_ranking_errors(week)

	def get_aggregated_analyst_errors(self, week):
		db_key = "aggregated_analyst_stats_{}".format(week)
		aggregated_analyst_stats = self._db[db_key]
		cursor = aggregated_analyst_stats.find({}, {'_id': False})
		if cursor.count() > 0:
			return cursor[0]

		stats = self._get_weekly_ranking_errors(week)
		aggregated_stats = {}

		for stat in stats.values():
			for analyst, error in stat.items():
				if analyst not in aggregated_stats:
					aggregated_stats[analyst] = 0
				aggregated_stats[analyst] += error

		aggregated_analyst_stats.insert(aggregated_stats)
		aggregated_stats.pop('_id', None)
		return aggregated_stats

	def get_aggregated_season_stats(self):
		db_key = "aggregated_position_stats_{}".format(self._latest_week)
		aggregated_season_stats = self._db[db_key]
		cursor = aggregated_season_stats.find({}, {'_id': False})
		if cursor.count() > 0:
			return cursor[0]

		total_stats = {}
		for week in range(1, self._latest_week+1):
			weekly_stats = self._get_weekly_ranking_errors(week)
			# Combine stats
			if not bool(total_stats):
				total_stats = copy.deepcopy(weekly_stats)
			else:
				for position in total_stats.keys():
					for analyst in total_stats[position]:
						total_stats[position][analyst] += weekly_stats[position][analyst]

		aggregated_season_stats.insert(total_stats)
		total_stats.pop('_id', None)
		return total_stats

	def _get_weekly_ranking_errors(self, week):
		if not self._is_valid_week(week):
			raise ValueError("Invalid Week Provided")

		# Check to see if data exists
		db_key = self._get_db_key(week)
		stat_collection = self._db[db_key]
		cursor = stat_collection.find({}, {'_id': False})
		if cursor.count() > 0:
			return cursor[0]

		# Retrieve data if it doesn't exist
		data = self._rf.fetch_rankings_by_week(week)
		weekly_errors = {}

		for position in constants.POSITIONS:
			errors = {}
			leaders = self._lf.fetch_weekly_leaders(week, position)
			# Use root mean squared error as the error estimate
			for analyst in constants.ANALYSTS:
				total_error = 0

				position_ranks = data.get_position_rankings_by_analyst(position, analyst)
				for rank in range(len(leaders)):
					player = leaders[rank]
					predicted_rank = position_ranks.loc[position_ranks['PLAYER'] == player]
					try:
						analyst_rank = predicted_rank.iloc[0][analyst]
						total_error += ((analyst_rank - rank) ** 2)
					except IndexError:
						max_rank = constants.MAX_RANKS[position]
						total_error += ((max_rank - rank) ** 2)
				rmse = np.sqrt(total_error / len(leaders))
				errors[analyst] = rmse

			position_name = constants.POSITION_MAP[position]
			weekly_errors[position_name] = self._get_nrmsd(errors)

		# Persist data
		stat_collection.insert(weekly_errors)
		weekly_errors.pop('_id', None)
		return weekly_errors

	def _get_db_key(self, week):
		return "week_{}".format(week)

	# Calculate normalized root mean square deviation
	# https://en.wikipedia.org/wiki/Root-mean-square_deviation#Normalized_root-mean-square_deviation
	def _get_nrmsd(self, analyst_errors):
		mean = np.mean(list(analyst_errors.values()))
		nrmsd_errors = { k: v / mean for k, v in analyst_errors.items() }
		return nrmsd_errors

	def _is_valid_week(self, week):
		try:
			week_val = int(week)
			return week_val > 0 and week_val <= self._latest_week
		except ValueError:
			return False

	def _find_latest_week(self):
		start_date = datetime.strptime(constants.SEASON_START, "%b %d %Y")
		weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=datetime.now())
		num_weeks = weeks.count()
		return num_weeks

	def _is_valid_position(self, position):
		try:
			position_val = int(position)
			return position_val in constants.POSITIONS
		except ValueError:
			return False
