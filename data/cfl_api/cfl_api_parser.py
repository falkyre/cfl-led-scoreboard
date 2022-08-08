"""
Module that is used for getting basic information about a game
such as the scoreboard and the box score.
"""

from cfl_api.utils import convert_time
import cfl_api.data
import cfl_api.object


def get_all_games():
    """
        Return the scoreboard information for games matching the parameters
        as a dictionary.
    """
    data = cfl_api.data.get_all_games()

    if data:
        games = {}
        for game in data:
            output = {
                'id': int(game['game_id']),  # ID of the game
                'date': game['date_start'],  # Date and time of the game
                'home_team_abrev': game['team_2']['abbreviation'],  # Home team name abbreviation
                'home_team_name': game['team_2']['nickname'],  # Home team name
                'home_team_id': game['team_2']['team_id'],  # ID of the Home team
                'home_score': int(game['team_2']['score']),  # Home team goals
                'away_team_abrev': game['team_1']['abbreviation'],  # Away team name abbreviation
                'away_team_id': game['team_1']['team_id'],  # ID of the Away team
                'away_team_name': game['team_1']['nickname'],  # Away team name
                'away_score': int(game['team_1']['score']),  # Away team goals
                'down': game['event_status']['down'],   # Current down.
                'spot': game['event_status']['yards_to_go'],   # Current yards to go.
                'time': f"{game['event_status']}:{game['event_status']['seconds']}",
                'quarter': game['event_status']['quarter'],
                'over': bool(not game['event_status']['is_active']),
                'redzone': game['event_status']['yards_to_go'] <= 20,
                'possession': True,
                'game_type': game['event_type']['name'],  # Preseason, Regular Season, Playoffs, Grey Cup, Exhibition
                'state': game['event_status']['name'],   # State of the game.
                'week': int(game['week']),
                'season': int(game['season']),
                'attendance': int(game['attendance']),
                'boxscore': game['boxscore'], # Dictionary with boxscores of games.
                'plays': game['play_by_play'],  # Dictionary of all the plays of the game.
            }

            # put this dictionary into the larger dictionary
            games[game.id] = output
        return games
    else:
        return []


def overview(game_id):
    data = cfl_api.data.get_overview(game_id)
    game = data

    output = {
        'id': int(game['game_id']),  # ID of the game
        'date': game['date_start'],  # Date and time of the game
        'home_team_abrev': game['team_2']['abbreviation'],  # Home team name abbreviation
        'home_team_name': game['team_2']['nickname'],  # Home team name
        'home_team_id': game['team_2']['team_id'],  # ID of the Home team
        'home_score': int(game['team_2']['score']),  # Home team goals
        'away_team_abrev': game['team_1']['abbreviation'],  # Away team name abbreviation
        'away_team_id': game['team_1']['team_id'],  # ID of the Away team
        'away_team_name': game['team_1']['nickname'],  # Away team name
        'away_score': int(game['team_1']['score']),  # Away team goals
        'down': game['event_status']['down'],   # Current down.
        'spot': game['event_status']['yards_to_go'],   # Current yards to go.
        'time': f"{game['event_status']}:{game['event_status']['seconds']}",
        'quarter': game['event_status']['quarter'],
        'over': bool(not game['event_status']['is_active']),
        'redzone': game['event_status']['yards_to_go'] <= 20,
        'possession': True,
        'game_type': game['event_type']['name'],  # Preseason, Regular Season, etc
        'state': game['event_status']['name'],   # State of the game.
        'week': int(game['week']),
        'season': int(game['season']),
        'attendance': int(game['attendance']),
        'boxscore': game['boxscore'], # Dictionary with boxscores of games.
        'plays': game['play_by_play'],  # Dictionary of all the plays of the game.
    }
    return output
