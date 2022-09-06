"""
Module that is used for getting basic information about a game
such as the scoreboard and the box score.
"""
from datetime import datetime, timedelta
import dotenv
import requests
import debug
from . import scoreboard_config as sb_config
from . import data as Data
from utils import args

ENV = dotenv.dotenv_values('.env')
API_KEY = ENV['CFL_API_KEY']  # Get yours here: https://api.cfl.ca/key-request

ARGS = args()
SB_CONFIG = sb_config.ScoreboardConfig("config", ARGS)
TESTING = SB_CONFIG.testing

REQUEST_TIMEOUT = 5
NETWORK_RETRY_SLEEP_TIME = 10.0

# get current datetime
CURRENT_DATE = datetime.today()
ISO_CURRENT_DATE = CURRENT_DATE.isoformat()
CURRENT_YEAR = CURRENT_DATE.year

BASE_URL = "http://api.cfl.ca"
GAME_OVERVIEW_URL = "{base}/v1/games/{year}/game/{game_id}?include=play_by_play&key={api_key}"
SCHEDULE_URL = "{base}/v1/games/{year}?key={api_key}{week_filter}"
SEASON_URL = "{base}/v1/seasons?key={api_key}"
STANDINGS_URL = "{base}/v1/standings/{year}?key={api_key}"
XO_STANDINGS_URL = "{base}/v1/standings/crossover/{year}?key={api_key}"
PLAYER_URL = "{base}/v1/players/{player_id}?key={api_key}"
TEAMS_URL = "{base}/v1/teams?key={api_key}"

# Possible CFL game Statuses
''' CFL
    1: Pre-Game
    2: In-Progress
    4: Final
    6: Postponed
    9: Cancelled
'''

# Possible CFL Event Types
'''
    0: Preseason
    1: Regular Season
    2: Playoffs
    3: Grey Cup
    4: Exhibition
'''


# Ref: SCHEDULE_URL = "{base}/v1/games?filter[date_start][ge]={day}" + API_KEY
# Note: USED DAY. Will need filtering for this in CFL.
def get_all_games(day=ISO_CURRENT_DATE, year=CURRENT_YEAR):
   try:
      data = { "data": [
            {
               "game_id":2172,
               "date_start":"2015-06-08T19:30:00-04:00",
               "game_number":1,
               "week":1,
               "season":2015,
               "attendance":0,
               "event_type":{
                  "event_type_id":0,
                  "name":"Preseason",
                  "title":""
               },
               "event_status":{
                  "event_status_id":4,
                  "name":"Final",
                  "is_active":False,
                  "quarter":4,
                  "minutes":0,
                  "seconds":0,
                  "down":3,
                  "yards_to_go":13
               },
               "venue":{
                  "venue_id":4,
                  "name":"Tim Hortons Field"
               },
               "weather":{
                  "temperature":21,
                  "sky":"Overcast",
                  "wind_speed":"",
                  "wind_direction":"6km\/h SW",
                  "field_conditions":"Dry"
               },
               "coin_toss":{
                  "coin_toss_winner":"",
                  "coin_toss_winner_election":"Ottawa won coin toss and elected to receive."
               },
               "tickets_url":"http:\/\/www.ticats.ca\/tickets\/",
               "team_1":{
                  "team_id":6,
                  "location":"Ottawa",
                  "nickname":"Redblacks",
                  "abbreviation":"OTT",
                  "score":10,
                  "venue_id":6,
                  "linescores":[
                     {
                        "quarter":1,
                        "score":0
                     },
                     {
                        "quarter":2,
                        "score":0
                     },
                     {
                        "quarter":3,
                        "score":0
                     },
                     {
                        "quarter":4,
                        "score":10
                     }
                  ],
                  "is_at_home":False,
                  "is_winner":False
               },
               "team_2":{
                  "team_id":4,
                  "location":"Hamilton",
                  "nickname":"Tiger-Cats",
                  "abbreviation":"HAM",
                  "score":37,
                  "venue_id":4,
                  "linescores":[
                     {
                        "quarter":1,
                        "score":7
                     },
                     {
                        "quarter":2,
                        "score":13
                     },
                     {
                        "quarter":3,
                        "score":14
                     },
                     {
                        "quarter":4,
                        "score":3
                     }
                  ],
                  "is_at_home":True,
                  "is_winner":True
               }
            },
            {
               "game_id":2173,
               "date_start":"2015-06-09T19:30:00-04:00",
               "game_number":2,
               "week":2,
               "season":2015,
               "attendance":5000,
               "event_type":{
                  "event_type_id":0,
                  "name":"Preseason",
                  "title":""
               },
               "event_status":{
                  "event_status_id":4,
                  "name":"Final",
                  "is_active":False,
                  "quarter":4,
                  "minutes":0,
                  "seconds":0,
                  "down":1,
                  "yards_to_go":10
               },
               "venue":{
                  "venue_id":10,
                  "name":"Toronto: Varsity Stadium"
               },
               "weather":{
                  "temperature":16,
                  "sky":"Cloudy",
                  "wind_speed":"",
                  "wind_direction":"5 km per  hour",
                  "field_conditions":"Dry, artificial turf"
               },
               "coin_toss":{
                  "coin_toss_winner":"",
                  "coin_toss_winner_election":"Coin toss: Toronto won the toss and elected to receive."
               },
               "tickets_url":"http:\/\/www.argonauts.ca\/tickets\/",
               "team_1":{
                  "team_id":9,
                  "location":"Winnipeg",
                  "nickname":"Blue Bombers",
                  "abbreviation":"WPG",
                  "score":34,
                  "venue_id":9,
                  "linescores":[
                     {
                        "quarter":1,
                        "score":3
                     },
                     {
                        "quarter":2,
                        "score":10
                     },
                     {
                        "quarter":3,
                        "score":14
                     },
                     {
                        "quarter":4,
                        "score":7
                     }
                  ],
                  "is_at_home":False,
                  "is_winner":True
               },
               "team_2":{
                  "team_id":8,
                  "location":"Toronto",
                  "nickname":"Argonauts",
                  "abbreviation":"TOR",
                  "score":27,
                  "venue_id":8,
                  "linescores":[
                     {
                        "quarter":1,
                        "score":6
                     },
                     {
                        "quarter":2,
                        "score":0
                     },
                     {
                        "quarter":3,
                        "score":8
                     },
                     {
                        "quarter":4,
                        "score":13
                     }
                  ],
                  "is_at_home":True,
                  "is_winner":False
               }
            },
            # ... games continue ... 
         ],
         "errors":[
      
         ],
         "meta":{
            "copyright":"Copyright 2017 Canadian Football League."
         }
      }
      
      sched = data
      
      if not TESTING:
         req_url = SCHEDULE_URL.format(base=BASE_URL, year=year, api_key=API_KEY, week_filter=f'&filter[week][eq]={get_current_week()}')
         debug.info(f'Fetching games from: {req_url}')
         data = requests.get(req_url, timeout=REQUEST_TIMEOUT)
         sched = data.json()
         
      if len(sched['errors']) > 0:
            errors = []
            for error in sched['errors']:
               errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
            raise ValueError(errors)
         
      games = []
      for game in sched['data']:
         output = {
               'id': game['game_id'],  # ID of the game
               'date': game['date_start'],  # Date and time of the game
               'game_type': game['event_type']['name'],  # Preseason, Regular Season, Playoffs, Grey Cup, Exhibition
               'week': game['week'],
               'season': game['season'],
               'attendance': game['attendance'],
               
               'state': game['event_status']['name'],   # State of the game.
               'over': game['event_status']['is_active'],
               'quarter': game['event_status']['quarter'],
               'time': f"{game['event_status']['minutes']}:{game['event_status']['seconds']}",
               
               'down': game['event_status']['down'],   # Current down.
               'spot': game['event_status']['yards_to_go'],   # Current yards to go.
               
               'home_team_abbrev': game['team_2']['abbreviation'],  # Home team name abbreviation
               'home_team_name': game['team_2']['nickname'],  # Home team name
               'home_team_id': game['team_2']['team_id'],  # ID of the Home team
               'home_score': game['team_2']['score'],  # Home team goals
               
               'away_team_abbrev': game['team_1']['abbreviation'],  # Away team name abbreviation
               'away_team_id': game['team_1']['team_id'],  # ID of the Away team
               'away_team_name': game['team_1']['nickname'],  # Away team name
               'away_score': game['team_1']['score'],  # Away team goals
         }
         # put this dictionary into the larger dictionary
         games.append(output)
      return games
   except requests.exceptions.RequestException as e:
      debug.error(e)
      raise ValueError(e)


def get_current_season(year=CURRENT_YEAR):
   if not hasattr(Data, 'current_season'):
      try:
         req_url = SEASON_URL.format(base=BASE_URL, year=year, api_key=API_KEY)
         debug.info(f'Fetching season info from: {req_url}')
         data = requests.get(req_url, timeout=REQUEST_TIMEOUT)
         cs = data.json()
         
         if len(cs['errors']) > 0:
               errors = []
               for error in cs['errors']:
                  errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
               raise ValueError(errors)
            
         Data.current_season = cs['data']['current']['season']
         return [cs['data']['current']['season'], cs['data']['current']['week']]
      
      except requests.exceptions.RequestException as e:
         raise ValueError(e)
   else:
      debug.info(f'Found current season in data: {Data.current_season}')
      return Data.current_season

# Ref: SEASON_URL = "{base}/v1/seasons"
def get_current_week():
   if not hasattr(Data, 'current_week'):
      try:
         req_url = SEASON_URL.format(base=BASE_URL, api_key=API_KEY)
         debug.info(f'Fetching week info from: {req_url}')
         data = requests.get(req_url, timeout=REQUEST_TIMEOUT)
         cs = data.json()
         if len(cs['errors']) > 0:
               errors = []
               for error in cs['errors']:
                  errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
               raise ValueError(errors)
         Data.current_week = cs['data']['current']['week']
         return cs['data']['current']['week']
      except requests.exceptions.RequestException as e:
         raise ValueError(e)
   else:
      debug.info(f'Found current week in data: {Data.current_week}')
      return Data.current_week

# Ref: TEAMS_URL = "{base}/v1/teams"
def get_teams():
   try:
      teams_url = TEAMS_URL.format(base=BASE_URL, api_key=API_KEY)
      debug.info(f'Fetching teams from: {teams_url}')
      data = requests.get(teams_url, timeout=REQUEST_TIMEOUT)
      teams = data.json()
      if len(teams['errors']) > 0:
            errors = []
            for error in teams['errors']:
               errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
            raise ValueError(errors)
      return teams['data']
   except requests.exceptions.RequestException as e:
      raise ValueError(e)

# Ref: PLAYER_URL = "{base}/v1/players/{player_id}"
def get_player(cfl_central_id):
   try:
      data = requests.get(PLAYER_URL.format(base=BASE_URL, player_id=cfl_central_id, api_key=API_KEY), timeout=REQUEST_TIMEOUT)
      player = data.json()
      if len(player['errors']) > 0:
            errors = []
            for error in player['errors']:
               errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
            raise ValueError(errors)
      return player['data'][0]
   except requests.exceptions.RequestException as e:
      raise ValueError(e)

# Ref: GAME_OVERVIEW_URL = "{base}/v1/games?filter[game_id][eq]={game_id}&include=boxscore,play_by_play" + API_KEY
# Game Overview
def get_overview(game_id):
   try:
      req_url = GAME_OVERVIEW_URL.format(base=BASE_URL, game_id=game_id, year=CURRENT_YEAR, api_key=API_KEY)
      debug.info(f'Fetching game overview for game_id={game_id} from: {req_url}')
      data = requests.get(req_url, timeout=REQUEST_TIMEOUT)
      game = data.json()
      
      if len(game['errors']) > 0:
         errors = []
         for error in game['errors']:
            errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
         raise ValueError(errors)
      
      output = {
               'id': game['data'][0]['game_id'],  # ID of the game
               'date': game['data'][0]['date_start'],  # Date and time of the game
               'game_type': game['data'][0]['event_type']['name'],  # Preseason, Regular Season, Playoffs, Grey Cup, Exhibition
               'week': game['data'][0]['week'],
               'season': game['data'][0]['season'],
               'attendance': game['data'][0]['attendance'],
               
               'state': game['data'][0]['event_status']['name'],   # State of the game.
               'over': game['data'][0]['event_status']['is_active'],
               'quarter': game['data'][0]['event_status']['quarter'],
               'time': f"{game['data'][0]['event_status']['minutes']:02}:{game['data'][0]['event_status']['seconds']:02}",
               
               'play_by_play': game['data'][0]['play_by_play'],
               'possession': game['data'][0]['play_by_play'][-1]['team_abbreviation'],
               'redzone': game['data'][0]['play_by_play'][-1]['is_in_red_zone'],
               'down': game['data'][0]['event_status']['down'],   # Current down.
               'spot': game['data'][0]['event_status']['yards_to_go'],   # Current yards to go.
               
               'home_team_abbrev': game['data'][0]['team_2']['abbreviation'],  # Home team name abbreviation
               'home_team_name': game['data'][0]['team_2']['nickname'],  # Home team name
               'home_team_id': game['data'][0]['team_2']['team_id'],  # ID of the Home team
               'home_score': game['data'][0]['team_2']['score'],  # Home team goals
               
               'away_team_abbrev': game['data'][0]['team_1']['abbreviation'],  # Away team name abbreviation
               'away_team_id': game['data'][0]['team_1']['team_id'],  # ID of the Away team
               'away_team_name': game['data'][0]['team_1']['nickname'],  # Away team name
               'away_score': game['data'][0]['team_1']['score'],  # Away team goals
      }
      # put this dictionary into the larger dictionary
      return output
   
   except requests.exceptions.RequestException as e:
      raise ValueError(e)

# Ref: STANDINGS_URL = "{base}/v1/standings/{year}"
# def get_standings(year=get_current_season()):
#     try:
#         data = requests.get(STANDINGS_URL.format(base=BASE_URL, year=year, api_key=API_KEY), timeout=REQUEST_TIMEOUT)
#         standings = data.json()
#         if len(standings['errors']) > 0:
#             errors = []
#             for error in standings['errors']:
#                 errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
#             raise ValueError(errors)
#         return standings['data']
#     except requests.exceptions.RequestException as e:
#         raise ValueError(e)

# Ref: STANDINGS_URL = "{base}/v1/standings/crossover/{year}"
# def get_standings_crossover(year=2014, data=xo):
#     try:
#         # data = requests.get(XO_STANDINGS_URL.format(base=BASE_URL, year=year, api_key=API_KEY), timeout=REQUEST_TIMEOUT)
#         xo = data
#         if len(xo['errors']) > 0:
#             errors = []
#             for error in xo['errors']:
#                 errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
#             raise ValueError(errors)
#         return xo['data']
#     except requests.exceptions.RequestException as e:
#         raise ValueError(e)
   
