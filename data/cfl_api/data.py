from datetime import datetime, timedelta
import time as t
from tzlocal import get_localzone
from . import cfl_api_parser as cflparser
import debug
from .object import MultiLevelObject


class Data:
    def __init__(self, config):
        # Save the parsed config
        self.config = config

        # Flag to determine when to refresh data
        self.needs_refresh = True

        # What game do we want to start on?
        self.current_game_index = 0
        self.current_division_index = 0

        # Parse today's date and see if we should use today or yesterday
        self.get_current_date()

        # Fetch the teams info
        self.refresh_games()
        # self.refresh_games(self.current_game()['id'])
        self.showing_preferred_game()

        # self.playoffs = cflparser.is_playoffs()
        # self.games = cflparser.get_all_games()
        # self.game = self.choose_game()
        # self.gametime = self.get_gametime()
        # self.scores = {}

    def get_current_date(self):
        return datetime.now(get_localzone())

    # Get All Games
    def refresh_games(self, game_id=None):
        attempts_remaining = 5
        while attempts_remaining > 0:
            if game_id is None:
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
                except ValueError as e:
                    self.network_issues = True
                    debug.error("ValueError while refreshing master list of games. {} retries remaining.".format(attempts_remaining))
                    debug.error("Error(s): {}".format(e))
                    attempts_remaining -= 1
                    t.sleep(cflparser.NETWORK_RETRY_SLEEP_TIME)
                except Exception as e:
                    self.network_issues = True
                    debug.error("Networking error while refreshing the master list of games. {} retries remaining.".format(attempts_remaining))
                    debug.error("Exception(s): {}".format(e))
                    attempts_remaining -= 1
                    t.sleep(cflparser.NETWORK_RETRY_SLEEP_TIME)
            else:
                try:
                    self.game = cflparser.get_overview(game_id)
                    self.game_refresh_time = t.time()
                    self.needs_refresh = False
                    self.network_issues = False
                    break
                except ValueError as e:
                    self.network_issues = True
                    debug.error("ValueError while refreshing single game overview - ID: {}. {} retries remaining.".format(game_id, attempts_remaining))
                    debug.error("Error(s): {}".format(e))
                    attempts_remaining -= 1
                    t.sleep(cflparser.NETWORK_RETRY_SLEEP_TIME)
                except Exception as e:
                    self.network_issues = True
                    debug.error("Networking error while refreshing single game overview - ID: {}. {} retries remaining.".format(game_id, attempts_remaining))
                    debug.error("Exception(s): {}".format(e))
                    attempts_remaining -= 1
                    t.sleep(cflparser.NETWORK_RETRY_SLEEP_TIME)

        # If we run out of retries, just move on to the next game
        if attempts_remaining <= 0 and self.config.rotation_enabled:
            self.advance_to_next_game()

    def get_gametime(self):
        tz_diff = t.timezone if (t.localtime().tm_isdst == 0) else t.altzone
        gametime = datetime.strptime(self.games[self.current_game_index]['date'], "%Y-%m-%dT%H:%M:%S%z") + timedelta(hours=(tz_diff / 60 / 60 * -1))
        return gametime

    def current_game(self):
        return self.games[self.current_game_index]
    
    # figure this out later heh
    def showing_preferred_game(self):
        showing_preferred_team = self.config.preferred_teams[0] in [self.current_game()['home_team_abbrev'], self.current_game()['away_team_abbrev']]
        if showing_preferred_team and self.game['state'] == 'In-Progress':
            debug.info("showing_preferred_game = true")
            return True
        
        debug.info("showing_preferred_game = false")
        return False

    def advance_to_next_game(self):
        self.current_game_index = self.__next_game_index()
        return self.current_game()

    def __filter_list_of_games(self, games, teams):
        return list(game for game in games if set([game['away_team_abbrev'], game['home_team_abbrev']]).intersection(set(teams)))

    def __next_game_index(self):
        counter = self.current_game_index + 1
        if counter >= len(self.games):
            counter = 0
        return counter
