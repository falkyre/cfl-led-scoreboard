import requests
import datetime

'''
TODO: Grab API key from config.json
'''

# Get yours here: https://api.cfl.ca/key-request
API_KEY = "?key=1zKYcrJgGUpiSsX8rvyaxssH2W9VHeBu"
REQUEST_TIMEOUT = 5

# get current datetime
CURRENT_DATE = datetime.date.today()
ISO_CURRENT_DATE = CURRENT_DATE.isoformat()

BASE_URL = "http://api.cfl.ca"
GAME_OVERVIEW_URL = "{base}/v1/games?filter[game_id][eq]={game_id}&include=boxscore,play_by_play" + API_KEY
SCHEDULE_URL = "{base}/v1/games?filter[date_start][eq]={day}" + API_KEY
SEASON_URL = "{base}/v1/seasons" + API_KEY
STANDINGS_URL = "{base}/v1/standings/{year}" + API_KEY
# STANDINGS_WILD_CARD = STANDINGS_URL + "/wildCardWithLeaders"
XO_STANDINGS_URL = "{base}/v1/standings/crossover/{year}" + API_KEY
PLAYER_URL = "{base}/v1/players/{player_id}" + API_KEY
TEAMS_URL = "{base}/v1/teams" + API_KEY


# STATUS_URL = "{base}/v1/gameStatus"
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


# Ref: SEASON_URL = "{base}/v1/seasons"
def get_current_season():
    try:
        data = requests.get(SEASON_URL.format(base=BASE_URL), timeout=REQUEST_TIMEOUT)
        cs = data.json()
        if len(cs['errors']) > 0:
            errors = []
            for error in cs['errors']:
                errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
            raise ValueError(errors)
        return cs['data']['current']['season']
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


# Ref: SEASON_URL = "{base}/v1/seasons"
def get_current_week():
    try:
        data = requests.get(SEASON_URL.format(base=BASE_URL), timeout=REQUEST_TIMEOUT)
        cw = data.json()
        if len(cw['errors']) > 0:
            errors = []
            for error in cw['errors']:
                errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
            raise ValueError(errors)
        return cw['data']['current']['week']
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


# Ref: SCHEDULE_URL = "{base}/v1/games?filter[date_start][ge]={day}" + API_KEY
# Note: USED DAY. Will need filtering for this in CFL.
def get_schedule(day=ISO_CURRENT_DATE):
    try:
        data = requests.get(SCHEDULE_URL.format(base=BASE_URL, day=day), timeout=REQUEST_TIMEOUT)
        sched = data.json()
        if len(sched['errors']) > 0:
            errors = []
            for error in sched['errors']:
                errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
            raise ValueError(errors)
        return sched['data']
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


# Ref: TEAMS_URL = "{base}/v1/teams"
def get_teams():
    try:
        data = requests.get(TEAMS_URL.format(base=BASE_URL), timeout=REQUEST_TIMEOUT)
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
        data = requests.get(PLAYER_URL.format(base=BASE_URL, player_id=cfl_central_id), timeout=REQUEST_TIMEOUT)
        player = data.json()
        if len(player['errors']) > 0:
            errors = []
            for error in player['errors']:
                errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
            raise ValueError(errors)
        return player['data']
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


# Ref: GAME_OVERVIEW_URL = "{base}/v1/games?filter[game_id][eq]={game_id}&include=boxscore,play_by_play" + API_KEY
# Game Overview
def get_overview(game_id):
    try:
        data = requests.get(GAME_OVERVIEW_URL.format(base=BASE_URL, game_id=game_id), timeout=REQUEST_TIMEOUT)
        game = data.json()
        if len(game['errors']) > 0:
            errors = []
            for error in game['errors']:
                errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
            raise ValueError(errors)
        return game['data'][0]
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


# Ref: STANDINGS_URL = "{base}/v1/standings/{year}"
def get_standings(year=get_current_season()):
    try:
        data = requests.get(STANDINGS_URL.format(base=BASE_URL, year=year), timeout=REQUEST_TIMEOUT)
        standings = data.json()
        if len(standings['errors']) > 0:
            errors = []
            for error in standings['errors']:
                errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
            raise ValueError(errors)
        return standings['data']
    except requests.exceptions.RequestException as e:
        raise ValueError(e)


# Ref: STANDINGS_URL = "{base}/v1/standings/crossover/{year}"
# def get_standings_crossover(year=2014, data=xo):
#     try:
#         # data = requests.get(XO_STANDINGS_URL.format(base=BASE_URL, year=year), timeout=REQUEST_TIMEOUT)
#         xo = data
#         if len(xo['errors']) > 0:
#             errors = []
#             for error in xo['errors']:
#                 errors.append("{} ERROR - ID:{} - {}".format(error['code'], error['id'], error['detail']))
#             raise ValueError(errors)
#         return xo['data']
#     except requests.exceptions.RequestException as e:
#         raise ValueError(e)
