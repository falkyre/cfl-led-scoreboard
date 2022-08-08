import requests
import datetime
import dotenv
import pytz
import debug
from datetime import datetime, timedelta
import time as t
from . import cfl_api_parser as cflparser

ENV = dotenv.dotenv_values('.env')

API_KEY = "?key=" + ENV['CFL_API_KEY']  # Get yours here: https://api.cfl.ca/key-request

REQUEST_TIMEOUT = 5
NETWORK_RETRY_SLEEP_TIME = 10.0

# get current datetime
CURRENT_DATE = datetime.today()
ISO_CURRENT_DATE = CURRENT_DATE.isoformat()

BASE_URL = "http://api.cfl.ca"
GAME_OVERVIEW_URL = "{base}/v1/games?filter[game_id][eq]={game_id}&include=boxscore,play_by_play" + API_KEY
SCHEDULE_URL = "{base}/v1/games?filter[date_start][eq]={day}" + API_KEY
SEASON_URL = "{base}/v1/seasons" + API_KEY
STANDINGS_URL = "{base}/v1/standings/{year}" + API_KEY
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



class Data:
    def __init__(self, config):
        # Save the parsed config
        self.config = config

        # Flag to determine when to refresh data
        self.needs_refresh = True

        # Parse today's date and see if we should use today or yesterday
        self.get_current_date()
        # Fetch the teams info
        self.refresh_games()

        # self.playoffs = cflparser.is_playoffs()
        # self.games = cflparser.get_all_games()
        # self.game = self.choose_game()
        # self.gametime = self.get_gametime()

        # What game do we want to start on?
        self.current_game_index = 0
        self.current_division_index = 0
        # self.scores = {}

    def get_current_date(self):
        return datetime.now(pytz.timezone('America/Toronto'))

    def refresh_game(self):
        self.game = self.choose_game()
        self.needs_refresh = False

    def refresh_games(self):
        attempts_remaining = 5
        while attempts_remaining > 0:
            try:
                all_games = cflparser.get_all_games()
                if self.config.rotation_only_preferred:
                    self.games = self.__filter_list_of_games(all_games, self.config.preferred_teams)
                # if rotation is disabled, only look at the first team in the list of preferred teams
                elif not self.config.rotation_enabled:
                    self.games = self.__filter_list_of_games(all_games, [self.config.preferred_teams[0]])
                else:
                    self.games = all_games

                self.games_refresh_time = t.time()
                self.network_issues = False
                break
            except ValueError:
                self.network_issues = True
                debug.error("Value Error while refreshing master list of games. {} retries remaining.".format(attempts_remaining))
                debug.error("ValueError: Failed to refresh list of games")
                attempts_remaining -= 1
                t.sleep(NETWORK_RETRY_SLEEP_TIME)
            except Exception as e:
                self.network_issues = True
                debug.error("Networking error while refreshing the master list of games. {} retries remaining.".format(attempts_remaining))
                debug.error("Exception: {}".format(e))
                attempts_remaining -= 1
                t.sleep(NETWORK_RETRY_SLEEP_TIME)

    #     # If we run out of retries, just move on to the next game
        if attempts_remaining <= 0 and self.config.rotation_enabled:
            self.advance_to_next_game()

    def get_gametime(self):
        tz_diff = t.timezone if (t.localtime().tm_isdst == 0) else t.altzone
        gametime = datetime.strptime(self.games[self.current_game_index]['date'], "%Y-%m-%dT%H:%M:%S%z") + timedelta(hours=(tz_diff / 60 / 60 * -1))
        return gametime

    def current_game(self):
        return self.games[self.current_game_index]

    # def update_scores(self, homescore, awayscore):
    #     self.scores[self.current_game_index] = {'home': homescore, 'away': awayscore}

    # def get_current_scores(self):
    #     if self.scores[self.current_game_index]:
    #         return self.scores[self.current_game_index]
    #     else:
    #         return {'home': 0, 'away': 0}

    # def refresh_overview(self):
    #     attempts_remaining = 5
    #     while attempts_remaining > 0:
    #         try:
    #             self.__update_layout_state()
    #             self.needs_refresh = False
    #             self.print_overview_debug()
    #             self.network_issues = False
    #             break
    #         except URLError, e:
    #             self.network_issues = True
    #             debug.error("Networking Error while refreshing the current overview. {} retries remaining.".format(attempts_remaining))
    #             debug.error("URLError: {}".format(e.reason))
    #             attempts_remaining -= 1
    #             time.sleep(NETWORK_RETRY_SLEEP_TIME)
    #         except ValueError:
    #             self.network_issues = True
    #             debug.error("Value Error while refreshing current overview. {} retries remaining.".format(attempts_remaining))
    #             debug.error("ValueError: Failed to refresh overview for {}".format(self.current_game().game_id))
    #             attempts_remaining -= 1
    #             time.sleep(NETWORK_RETRY_SLEEP_TIME)

    #     # If we run out of retries, just move on to the next game
    #     if attempts_remaining <= 0 and self.config.rotation_enabled:
    #         self.advance_to_next_game()

    def advance_to_next_game(self):
        self.current_game_index = self.__next_game_index()
        return self.current_game()

    # def game_index_for_preferred_team(self):
    #     if self.config.preferred_teams:
    #         return self.__game_index_for(self.config.preferred_teams[0])
    #     else:
    #         return 0

    def __filter_list_of_games(self, games, teams):
        return list(game for game in games if set([game['away_team_abbrev'], game['home_team_abbrev']]).intersection(set(teams)))

    # def __game_index_for(self, team_name):
    #     team_index = 0
    #     print(self.games)
    #     # team_idxs = [i for i, game in enumerate(self.games) if team_name in [game.awayteam, game.hometeam]]
    #     for game in enumerate(self.games):
    #         print(game)
    #     return team_index

    def __next_game_index(self):
        counter = self.current_game_index + 1
        if counter >= len(self.games):
            counter = 0
        return counter

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
    def get_all_games(day=ISO_CURRENT_DATE):
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
    # def get_standings(year=get_current_season()):
    #     try:
    #         data = requests.get(STANDINGS_URL.format(base=BASE_URL, year=year), timeout=REQUEST_TIMEOUT)
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