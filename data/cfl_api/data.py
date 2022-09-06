from datetime import datetime, timedelta
import time as t
from tzlocal import get_localzone
from . import cfl_api_parser as cflparser
import debug


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

        # TODO: self.playoffs = cflparser.is_playoffs()
        
        self.current_week = None
        self.current_season = None
        self.get_season_info()
        
    
    def get_season_info(self):
        # Get current season & week
        [self.current_season, self.current_week] = cflparser.get_current_season(self.current_week)
        

    def get_current_date(self):
        return datetime.now(get_localzone())

    # Get All Games
# CHANGE gameid TO NONE
    def refresh_games(self, game_id=None):
        attempts_remaining = 5
        while attempts_remaining > 0:
            if game_id is None:
                try:
                    all_games = [game for game in cflparser.get_all_games()]

                    if self.config.rotation_only_preferred:
                        self.games = self.__filter_list_of_games(all_games, self.config.preferred_teams)
                        debug.info(f'Filtering games for preferred team - {self.config.preferred_teams}')

                    elif not self.config.rotation_only_preferred and not self.config.rotation_preferred_team_live_enabled:
                        self.games = self.__filter_list_of_games(all_games, self.config.preferred_teams)
                        debug.info(f'Filtering games for preferred teams - {self.config.preferred_teams}')
                        
                    else:
                        self.games = all_games
                        
                    self.games_refresh_time = t.time()
                    self.needs_refresh = False
                    self.network_issues = False
                    break

                except ValueError as e:
                    self.network_issues = True
                    debug.error(f"Error refreshing master list of games. {attempts_remaining} retries remaining.")
                    debug.error(f"Error(s): {e}")
                    attempts_remaining -= 1
                    t.sleep(cflparser.NETWORK_RETRY_SLEEP_TIME)

                except Exception as e:
                    self.network_issues = True
                    debug.error(f"Network error while refreshing the list of games. {attempts_remaining} retries remaining.")
                    debug.error(f"Exception(s): {e}")
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
                    debug.error(f"ValueError while refreshing single game overview - ID: {game_id}. {attempts_remaining} retries remaining.")
                    debug.error(f"Error(s): {e}")
                    attempts_remaining -= 1
                    t.sleep(cflparser.NETWORK_RETRY_SLEEP_TIME)

                except Exception as e:
                    self.network_issues = True
                    debug.error(f"Networking error while refreshing single game overview - ID: {game_id}. {attempts_remaining} retries remaining.")
                    debug.error(f"Exception(s): {e}")
                    attempts_remaining -= 1
                    t.sleep(cflparser.NETWORK_RETRY_SLEEP_TIME)

        # If we run out of retries, just move on to the next game
        if attempts_remaining <= 0 and self.config.rotation_enabled:
            self.advance_to_next_game()
    
    def get_gametime(self):
        tz_diff = t.timezone if (t.localtime().tm_isdst == 0) else t.altzone
#        gametime = datetime.strptime(self.games[self.current_game_index]['date'], "%Y-%m-%dT%H:%M:%S%z") + timedelta(hours=(tz_diff / 60 / 60 * -1))
        gametime = datetime.strptime(self.games[0]['date'], "%Y-%m-%dT%H:%M:%S%z") + timedelta(hours=(tz_diff / 60 / 60 * -1))
        return gametime

    def current_game(self):
        current_game = None
        if len(self.games) > 0:
            current_game = cflparser.get_overview(game_id=self.games[self.current_game_index]['id'])
            return current_game

    def showing_preferred_game(self):
        current_game = self.games[self.current_game_index]
        next_game = self.games[self.__next_game_index()]
        preferred_next_game = self.config.preferred_teams[0] in [next_game['home_team_abbrev'], next_game['away_team_abbrev']] and next_game['state'] == 'In-Progress'
        showing_preferred_team = False
        
        if len(self.config.preferred_teams) > 1:
            for team in self.config.preferred_teams:
                if team in [current_game['home_team_abbrev'], current_game['away_team_abbrev']] and current_game['state'] == 'In-Progress' and not preferred_next_game:
                    showing_preferred_team = True
        else:
            if self.config.preferred_teams[0] in [current_game['home_team_abbrev'], current_game['away_team_abbrev']] and current_game['state'] == 'In-Progress':
                    showing_preferred_team = True
            
        if current_game is not None and showing_preferred_team:
            debug.info("showing_preferred_game = true(Live!)")
            return True
        debug.info("showing_preferred_game = false (Not live.)")
        return False

    def advance_to_next_game(self):
        self.current_game_index = self.__next_game_index()

    def __filter_list_of_games(self, games, teams):
        filtered_games = [game for game in games if set([game['away_team_abbrev'], game['home_team_abbrev']]).intersection(set(teams))]
        return filtered_games

    def __next_game_index(self):
        counter = self.current_game_index + 1
        if counter >= len(self.games):
            counter = 0
        return counter
