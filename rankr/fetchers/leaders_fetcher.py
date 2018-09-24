import requests
import pandas as pd
import numpy as np

from bs4 import BeautifulSoup


class LeadersFetcher():
	def __init__(self, league_id):
		self.league_id = league_id

	def fetch_weekly_leaders(self, week, position):
		'''
		Fetches a ranked list of scoring leaders based on week and position
		'''
		params = {
			'leagueId': self.league_id, 
			'seasonId': 2018, 
			'scoringPeriodId': int(week),
			'slotCategoryId': int(position),
			'teamId': 1
		}
		r = requests.get('http://games.espn.com/ffl/leaders', params=params)
		data = self._format_data(r)
		player_list = data.values.ravel()
		return player_list

	def _format_data(self, response):
		# Read raw response into pandas
		soup = BeautifulSoup(response.content, 'html.parser')
		table = soup.find('table', class_='playerTableTable')
		df = pd.read_html(str(table), flavor='bs4')[0]

		# Extract relevant column
		df = df.iloc[2:, [0]].reset_index(drop=True)
		df.columns = ['Player']

		# Format player names
		df['Player'] = df['Player'].str.split(',').str[0]
		df['Player'] = df['Player'].str.replace('[^a-zA-Z]', '')
		return df
