"""
Module that is used for getting basic information about a game
such as the scoreboard and the box score.
"""

from .utils import convert_time
from . import data
from . import object


def get_all_games():
    """
        Return the scoreboard information for games matching the parameters
        as a dictionary.
    """
   # data = cfl_api.data.get_all_games()

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

    if data:
        games = []
        for game in data['data']:
            output = {
                'id': game['game_id'],  # ID of the game
                'date': game['date_start'],  # Date and time of the game
                'home_team_abbrev': game['team_2']['abbreviation'],  # Home team name abbreviation
                'home_team_name': game['team_2']['nickname'],  # Home team name
                'home_team_id': game['team_2']['team_id'],  # ID of the Home team
                'home_score': int(game['team_2']['score']),  # Home team goals
                'away_team_abbrev': game['team_1']['abbreviation'],  # Away team name abbreviation
                'away_team_id': game['team_1']['team_id'],  # ID of the Away team
                'away_team_name': game['team_1']['nickname'],  # Away team name
                'away_score': int(game['team_1']['score']),  # Away team goals
                'down': game['event_status']['down'],   # Current down.
                'spot': game['event_status']['yards_to_go'],   # Current yards to go.
                'time': f"{game['event_status']}:{game['event_status']['seconds']}",
                'quarter': game['event_status']['quarter'],
                'over': bool(not game['event_status']['is_active']),
                'redzone': game['event_status']['yards_to_go'] <= 20,
                # playbyplay, boxscores, possession to be added to get_single_game data! 
                # 'possession': game['play_by_play'][0]['team_abbreviation'],
                'game_type': game['event_type']['name'],  # Preseason, Regular Season, Playoffs, Grey Cup, Exhibition
                'state': game['event_status']['name'],   # State of the game.
                'week': int(game['week']),
                'season': int(game['season']),
                'attendance': int(game['attendance']),
            }

            # put this dictionary into the larger dictionary
            games.append(output)
        return games
    else:
        return []
    