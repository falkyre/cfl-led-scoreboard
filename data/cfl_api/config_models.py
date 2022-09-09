from __future__ import annotations
from typing import List
from enum import Enum
from pydantic import BaseModel, Field


class Rates(BaseModel):
    pregame: float = Field(default=15.0, ge=2)
    live: float = Field(default=15.0, ge=2)
    final: float = Field(default=15.0, ge=2)


class Rotation(BaseModel):
    enabled: bool = True
    only_preferred: bool = False
    rates: Rates
    while_preferred_team_live: bool = False


class Teams(str, Enum):
    BC="BC"
    CGY="CGY"
    EDM="EDM"
    HAM="HAM"
    MTL="MTL"
    OTT="OTT"
    SSK="SSK"
    TOR="TOR"
    WPG="WPG"
    

class ConfigModel(BaseModel):
    preferred_teams: List[Teams]
    rotation: Rotation
    data_refresh_rate: float = Field(default=15.0, ge=5)
    debug: bool = False
    testing: bool = False
    
    class Config:
        title = 'Config'
        use_enum_values = True
