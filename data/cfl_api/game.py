"""
Module that is used for getting basic information about a game
such as the scoreboard and the box score.
"""

from cfl_api.utils import convert_time
import cfl_api.data
import cfl_api.object


def scoreboard(day):
    """
        Return the scoreboard information for games matching the parameters
        as a dictionary.
    """
    data = cfl_api.data.get_schedule(day)

    if data:
        games_data = data
        games = {}
        for game in games_data:
            game_id = game['game_id']
            game_date = game['date_start']
            week = game['week']
            season = game['season']
            attendance = game['attendance']
            game_type = game['event_type']['name']

            home_team_id = int(game['team_2']['team_id'])
            home_team_name = game['team_2']['nickname']
            away_team_id = int(game['team_1']['team_id'])
            away_team_name = game['team_1']['nickname']
            home_score = game['team_2']['score']
            away_score = game['team_1']['score']

            status = game['event_status']
            status_code = game['event_status']['event_status_id']
            status_abstract_state = game['event_status']['name']
            team_1_linescore = game['team_1']['linescores']
            team_2_linescore = game['team_2']['linescores']

            output = {
                'game_id': game_id,
                'game_date': game_date,
                'week': week,
                'season': season,
                'attendance': attendance,
                'game_type': game_type,
                'home_team_id': home_team_id,
                'home_team_name': home_team_name,
                'away_team_id': away_team_id,
                'away_team_name': away_team_name,
                'home_score': home_score,
                'away_score': away_score,
                'status': status,
                'status_code': status_code,
                'status_abstract_state': status_abstract_state,
                # All the linescore information (quarters/scores)
                'linescore': {
                    "team_2": team_2_linescore,
                    "team_1": team_1_linescore,
                },
            }

            # put this dictionary into the larger dictionary
            games[game_id] = output
        return games
    else:
        return []


class GameScoreboard(object):

    def __init__(self, data):
        # loop through data
        for x in data:
            # set information as correct data type
            try:
                setattr(self, x, int(data[x]))
            except ValueError:
                try:
                    setattr(self, x, float(data[x]))
                except ValueError:
                    # string if not number
                    setattr(self, x, str(data[x]))
            except TypeError:
                obj = cfl_api.object.Object(data[x])
                setattr(self, x, obj)

        # calculate the winning team
        if self.home_score > self.away_score:
            self.w_team = self.home_team_id
            self.l_team = self.away_team_id
        elif self.away_score > self.home_score:
            self.w_team = self.away_team_id
            self.l_team = self.home_team_id

        self.full_date = convert_time(self.game_date).strftime("%Y-%m-%d")
        self.start_time = convert_time(self.game_date).strftime("%I:%M")

    def __str__(self):
        return ('{0.away_team_name} ({0.away_score}) VS '
                '{0.home_team_name} ({0.home_score})').format(self)

    def __repr__(self):
        return self.__str__()


def overview(game_id):
    data = cfl_api.data.get_overview(game_id)
    game = data

    output = {
        'id': int(game['game_id']),  # ID of the game
        'game_date': game['date_start'],  # Date and time of the game
        'week': int(game['week']),
        'season': int(game['season']),
        'attendance': int(game['attendance']),
        'game_type': game['event_type']['name'],  # Type of game ("R" for Regular season, "P" for Post season or playoff)
        'time_stamp': game['time_stamp'],  # Last time the data was refreshed (UTC)
        'status': game['event_status'],   # Status of the game.
        'away_team_id': game['team_1']['team_id'],  # ID of the Away team
        'away_team_name': game['team_1']['nickname'],  # Away team name
        'away_team_abrev': game['team_1']['abbreviation'],  # Away team name abbreviation
        'away_score': int(game['team_1']['score']),  # Away team goals
        'home_team_id': game['team_2']['team_id'],  # ID of the Home team
        'home_team_name': game['team_2']['nickname'],  # Home team name
        'home_team_abrev': game['team_2']['abbreviation'],  # Home team name abbreviation
        'home_score': int(game['team_2']['score']),  # Home team goals
        # All the linescore information (quarters/scores)
        'linescore': {
            "home": game['team_2']['linescores'],
            "away": game['team_1']['linescores'],
        },
        # All the detailed boxscore information
        'boxscore': game['boxscore'],
        'plays': game['play_by_play'],  # Dictionary of all the plays of the game.
    }
    return output


class Overview(object):
    def __init__(self, data):
        # loop through data
        for x in data:
            # set information as correct data type
            try:
                setattr(self, x, int(data[x]))
            except ValueError:
                try:
                    setattr(self, x, float(data[x]))
                except ValueError:
                    # string if not number
                    setattr(self, x, str(data[x]))
            except TypeError:
                obj = cfl_api.object.Object(data[x])
                setattr(self, x, obj)

        # calculate the winning team
        if self.home_score > self.away_score:
            self.w_team = self.home_team_id
            self.w_score = self.home_score
            self.l_team = self.away_team_id
            self.l_score = self.away_score
        elif self.away_score > self.home_score:
            self.w_team = self.away_team_id
            self.w_score = self.away_score
            self.l_team = self.home_team_id
            self.l_score = self.home_score
