import operator
import numpy as np
import rankr.constants as constants

from datetime import datetime
from dateutil import rrule
from rankr.fetchers.rankings_fetcher import RankingsFetcher
from rankr.fetchers.leaders_fetcher import LeadersFetcher


class Analyzer():
	def __init__(self, league_id):
		self._league_id = league_id
		self._rf = RankingsFetcher(self._league_id)
		self._lf = LeadersFetcher(self._league_id)
		self._latest_week = self._find_latest_week()

	def get_ranking_errors(self, week, position):
		if not self._is_valid_week(week):
			raise ValueError("Invalid Week Provided")

		if not self._is_valid_position(position):
			raise ValueError("Invalid Position Provided")

		data = self._rf.fetch_rankings_by_week(week)
		leaders = self._lf.fetch_weekly_leaders(week, position)

		errors = {}
		# Use mean squared error as the error estimate
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
			mse = total_error / len(leaders)
			errors[analyst] = mse

		return errors

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
