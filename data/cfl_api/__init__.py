import cfl_api.game
import cfl_api.info


def day(day):
    """
        Return a list of games for a certain day.
    """
    # get data
    data = cfl_api.game.scoreboard(day)
    return [cfl_api.game.GameScoreboard(data[x]) for x in data]


def teams():
    """Return list of Info objects for each team"""
    return [cfl_api.info.TeamInfo(x) for x in cfl_api.info.team_info()]

def player(playerId):
    """Return an Info object of a player information"""
    return cfl_api.info.player_info(playerId)


def overview(game_id):
    """Return Overview object that contains game information."""
    return cfl_api.game.Overview(cfl_api.game.overview(game_id))


def game_status_info():
    return cfl_api.info.status()


def current_season_info():
    return cfl_api.info.current_season()


def standings():
    try:
        standings, wildcard = cfl_api.info.standings()
        return cfl_api.info.Standings(standings, wildcard)
    except:
        return False
