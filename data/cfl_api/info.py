import cfl_api.data
from cfl_api.object import Object, MultiLevelObject
from nameparser import HumanName
import debug


# TODO
def team_info():
    """
        Returns a list of team information dictionaries
    """
    teams_data = cfl_api.data.get_teams()
    teams = []

    for team in teams_data:
        try:
            team_data = team
            try:
                previous_game = team['previousGameSchedule']
            except:
                debug.log("No previous game detected for {}".format(team_data['full_name']))
                previous_game = False

            try:
                next_game = team['nextGameSchedule']
            except:
                debug.log("No next game detected for {}".format(team_data['full_name']))
                next_game = False

            # TEAM STATS

            output = {
                **team_info,
                'previous_game': previous_game,
                'next_game': next_game,
                'stats': stats,
            }

            # put this dictionary into the larger dictionary
            teams.append(output)
        except:
            debug.error("Missing data in current team info")

    return teams

def player_info(playerId):
    data = cfl_api.data.get_player(playerId)
    return MultiLevelObject(data)


def status():
    data = cfl_api.data.get_game_status()
    return data


def current_season():
    data = cfl_api.data.get_current_season()
    return data


# def playoff_info(season):
    data = cfl_api.data.get_playoff_data(season)
    parsed = data.json()
    season = parsed["season"]
    output = {'season': season}
    try:
        playoff_rounds = parsed["rounds"]
        rounds = {}
        for r in range(len(playoff_rounds)):
            rounds[str(playoff_rounds[r]["number"])] = MultiLevelObject(playoff_rounds[r])
        
        output['rounds'] = rounds
    except KeyError:
        debug.error("No data for {} Playoff".format(season))
        output['rounds'] = False

    try:
        default_round = parsed["defaultRound"]
        output['default_round'] = default_round
    except KeyError:
        debug.error("No default round for {} Playoff.".format(season))
        default_round = 1
        output['default_round'] = default_round

    return output

# def series_record(seriesCode, season):
    data = data = cfl_api.data.get_series_record(seriesCode, season)
    parsed = data.json()
    return parsed["data"]


def standings():
    data = cfl_api.data.get_standings().json()
    data_wildcard = cfl_api.data.get_standings_crossover().json()

    standing_records = {
        'east': [],
        'west': []
    }

    xo_records = {
        'east': [],
        'west': []
    }

    try:
        divisions = data['divisions']
        wildcards = data_wildcard['divisions']

        for division in divisions:
            standing_records[division] = division['standings']
        for division in wildcards:
            xo_records[division] = division['standings']

        return standing_records, xo_records

    except KeyError:
        return False, False


class Divisions:
    def __init__(self, east, west):
        if east:
            self.eastern = east
        if west:
            self.western = west


class CrossoverDivisions:
    def __init__(self, east, west, crossover, out):
        if east:
            self.eastern = east
        if west:
            self.western = west
        if crossover:
            self.crossover = crossover
        if out:
            self.out = out


class Standings(object):
    """
        Object containing all the standings data per team.

        Contains functions to return a dictionary of the data reorganised to represent
        different type of Standings.

    """
    def __init__(self, standing_records, xo_records):
        self.data = standing_records
        self.data_wildcard = xo_records
        self.get_division()
        self.get_crossover_divisions()

    def get_division(self):
        east = self.data['divisions']['east']
        west = self.data['divisions']['west']
        self.by_division = Divisions(east,  west)

    def get_crossover_divisions(self):
        east = self.data['divisions']['east']
        west = self.data['divisions']['west']
        crossover = self.data['divisions']['crossover']
        out = self.data['divisions']['out_of_playoffs']
        self.by_crossover = CrossoverDivisions(east, west, crossover, out)

class TeamInfo(Object):
    pass