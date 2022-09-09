import json
import os
from utils import get_file
import debug

from . import config_models
from pydantic import ValidationError

class ScoreboardConfig:
    try:
        def __init__(self, filename_base, args):
            json = self.__get_config(filename_base)
            config = config_models.ConfigModel.parse_obj(json)
            
            # Preferred Teams
            self.preferred_teams = config.preferred_teams

            # Rotation
            self.rotation_enabled = config.rotation.enabled
            self.rotation_only_preferred = config.rotation.only_preferred
            self.rotation_rates = config.rotation.rates.dict()
            self.rotation_preferred_team_live_enabled = config.rotation.while_preferred_team_live

            # Refresh Rate
            self.data_refresh_rate = config.data_refresh_rate
            
            # Debug
            self.debug = config.debug
            self.testing = config.testing
            
            # Rotation Settings
            self.rotation_rates = config.rotation.rates
            self.rotation_rates_pregame = self.rotation_rates.pregame
            self.rotation_rates_live = self.rotation_rates.live
            self.rotation_rates_final = self.rotation_rates.final

        def read_json(self, filename):
            # Find and return a json file

            j = {}
            path = get_file(filename)
            if os.path.isfile(path):
                j = json.load(open(path))
            return j

        def __get_config(self, base_filename):
            # Look and return config.json file

            filename = "{}.json".format(base_filename)
            reference_config = self.read_json(filename)

            return reference_config
        
    except ValidationError as e:
        debug.error(e)
