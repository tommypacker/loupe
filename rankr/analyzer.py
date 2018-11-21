import copy
import numpy as np
import constants

from datetime import datetime
from dateutil import rrule
from rankr.fetchers.rankings_fetcher import RankingsFetcher
from rankr.fetchers.leaders_fetcher import LeadersFetcher


class Analyzer():
	def __init__(self, league_id, db):
		self._league_id = league_id
		self._rf = RankingsFetcher(self._league_id)
		self._lf = LeadersFetcher(self._league_id)
		self._latest_week = self._find_latest_week()
		self._db = db

	def get_weekly_individual_errors(self, week):
		"""
		Returns the individual errors for each position for each analyst for a given week
		"""
		return self._get_weekly_ranking_errors(week)

	def get_season_individual_errors(self):
		"""
		Returns the total error each analyst has accrued for each position so far in the season
		"""
		db_key = "season_individual_errors_{}".format(self._latest_week)
		individual_errors = self._db[db_key]
		cursor = individual_errors.find({}, {'_id': False})
		if cursor.count() > 0:
			return cursor[0]

		season_errors = {}
		for week in range(1, self._latest_week+1):
			weekly_errors = self._get_weekly_ranking_errors(week)
			if not bool(season_errors):
				season_errors = copy.deepcopy(weekly_errors)
			else:
				for position in season_errors.keys():
					for analyst in constants.ANALYSTS:
						season_errors[position][analyst] += weekly_errors[position][analyst]

		individual_errors.insert(season_errors)
		season_errors.pop('_id', None)
		return season_errors

	def get_weekly_summed_errors(self, week):
		"""
		Returns the total error (sum over all positions) for each analyst for a given week
		"""
		db_key = "summed_errors_{}".format(week)

		# Check to see if errors have already been cached
		summed_errors = self._db[db_key]
		cursor = summed_errors.find({}, {'_id': False})
		if cursor.count() > 0:
			return cursor[0]

		# Sum total errors for all positions for each analyst
		errors = self._get_weekly_ranking_errors(week)
		aggregated_errors = {}
		for val in errors.values():
			for analyst, error in val.items():
				if analyst not in aggregated_errors:
					aggregated_errors[analyst] = 0
				aggregated_errors[analyst] += error

		summed_errors.insert(aggregated_errors)
		aggregated_errors.pop('_id', None)
		return aggregated_errors

	def get_season_summed_errors(self):
		"""
		Returns the total error (sum over all positions) for each analyst so far in the season
		"""
		db_key = "season_summed_errors_{}".format(self._latest_week)

		# Check to see if aggregated errors have already been cached
		season_summed_errors = self._db[db_key]
		cursor = season_summed_errors.find({}, {'_id': False})
		if cursor.count() > 0:
			return cursor[0]

		season_errors = {}
		for week in range(1, self._latest_week+1):
			weekly_errors = self.get_weekly_summed_errors(week)
			for analyst, error in weekly_errors.items():
				if analyst not in season_errors:
					season_errors[analyst] = 0
				season_errors[analyst] += error

		season_summed_errors.insert(season_errors)
		season_errors.pop('_id', None)
		return season_errors

	def _get_weekly_ranking_errors(self, week):
		"""
		Retrieves the individual errors of all positions for all analysts for a given week
		"""
		if not self._is_valid_week(week):
			raise ValueError("Invalid Week Provided")

		# Check to see if data exists
		db_key = self._get_db_key(week)
		error_collection = self._db[db_key]
		cursor = error_collection.find({}, {'_id': False})
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
		error_collection.insert(weekly_errors)
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