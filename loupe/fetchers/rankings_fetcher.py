import requests
import pandas as pd
import constants

from bs4 import BeautifulSoup


class RankingsFetcher():
	class Rankings():
		def __init__(self, df):
			self._df = df

		def get_position_rankings_by_analyst(self, position, analyst):
			analyst = analyst.upper()
			if analyst not in constants.ANALYSTS:
				raise ValueError("Invalid analyst provided")

			position_df = self._df.loc[self._df['POSITION'] == position]
			return position_df.sort_values(by=[analyst])[['PLAYER', analyst]]

	def __init__(self, league_id):
		self._league_id = league_id

	def fetch_rankings_by_week(self, week):
		columns = ['POSITION', 'PLAYER'] + constants.ANALYSTS
		df = pd.DataFrame(columns=columns)

		for position in constants.POSITIONS:
			params = {
				'leagueId': self._league_id,
				'seasonId': 2018, 
				'scoringPeriodId': int(week),
	 			'slotCategoryId': position,
				'teamId': 1,
				'view': 'ranks',
				'context': 'freeagency',
				'avail': -1
			}
			r = requests.get('http://games.espn.com/ffl/freeagency', params=params)
			position_df = self._format_data(r, position)
			df = df.append(position_df, sort=False)

		return self.Rankings(df)

	def _format_data(self, response, position):
		# Read raw response into pandas
		soup = BeautifulSoup(response.content, 'html.parser')
		table = soup.find('table', class_='playerTableTable')
		df = pd.read_html(str(table), flavor='bs4')[0]

		# Extract relevant columns
		df = df.iloc[2:, constants.ANALYST_COLS].reset_index(drop=True)
		df.columns = ['PLAYER'] + constants.ANALYSTS

		# Replace unranked values with the highest ranking + 1
		for analyst in constants.ANALYSTS:
			df[analyst] = df[analyst].replace('--', constants.MAX_RANKS[position]).astype('int')

		# Format player names
		df['PLAYER'] = df['PLAYER'].str.split(',').str[0].str.replace('[^a-zA-Z]', '')
		df['POSITION'] = position
		return df
