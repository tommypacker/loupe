import rankr.constants as constants


class PlayerRankings():
	def __init__(self, df):
		self._df = df

	def get_position_rankings_by_analyst(self, position, analyst):
		analyst = analyst.upper()
		if analyst not in constants.ANALYSTS:
			raise ValueError("Invalid analyst provided")

		position_df = self._df.loc[self._df['POSITION'] == position]
		return position_df.sort_values(by=[analyst])[['PLAYER', analyst]]
