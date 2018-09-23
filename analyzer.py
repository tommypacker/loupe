import operator
import numpy as np

import settings

from rankings_fetcher import RankingsFetcher
from leaders_fetcher import LeadersFetcher


class RankAnalyzer():
	def __init__(self, config):
		self._league_id = config['league_id']
		self._rf = RankingsFetcher(self._league_id)
		self._lf = LeadersFetcher(self._league_id)

	def get_ranking_errors(self, week, position):
		if not self._is_valid_week(week):
			raise ValueError("Invalid Week Provided")

		if not self._is_valid_position(position):
			raise ValueError("Invalid Position Provided")

		data = self._rf.fetch_rankings_by_week(week)
		leaders = self._lf.fetch_weekly_leaders(week, position)

		errors = {}
		# I use mean squared error as my error estimate
		for analyst in settings.ANALYSTS:
			total_error = 0

			position_ranks = data.get_position_rankings_by_analyst(position, analyst)
			for rank in range(len(leaders)):
				player = leaders[rank]
				predicted_rank = position_ranks.loc[position_ranks['PLAYER'] == player]
				try:
					analyst_rank = predicted_rank.iloc[0][analyst]
					total_error += ((analyst_rank - rank) ** 2)
				except IndexError:
					max_rank = settings.MAX_RANKS[position]
					total_error += ((max_rank - rank) ** 2)
			mse = total_error / len(leaders)
			errors[analyst] = mse

		return sorted(errors.items(), key=operator.itemgetter(1))

	# TODO: Find current week in season as upper bound
	def _is_valid_week(self, week):
		max_week = 17
		try:
			week_val = int(week)
			return week_val > 0 and week_val <= max_week
		except ValueError:
			return False

	def _is_valid_position(self, position):
		try:
			position_val = int(position)
			return position_val in settings.POSITIONS
		except ValueError:
			return False
