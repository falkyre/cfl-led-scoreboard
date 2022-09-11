from __future__ import annotations
from typing import List
from enum import Enum
from pydantic import BaseModel, Field


class Rates(BaseModel):
    pregame: float = Field(15.0, ge=2, description="Sets pre-game rotation rate. (Min=2.0)")
    live: float = Field(15.0, ge=2, description="Sets live-game rotation rate. (Min=2.0)")
    final: float = Field(15.0, ge=2, description="Sets post-game rotation rate. (Min=2.0)")


class Rotation(BaseModel):
    enabled: bool = Field(True, description="Enable rotation of games.")
    only_preferred: bool = Field(False, description="Rotate only preferred teams.")
    rates: Rates
    while_preferred_team_live: bool = Field(False, description="Rotate games while preferred team is live.")
    while_preferred_team_halftime: bool = Field(False, description="Rotate games while preferred teams is at halftime.")


class TeamEnum(str, Enum):
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
    preferred_teams: List[TeamEnum] = Field(["HAM"],  title="Preferred Teams", description="List of preferred teams to display. First is priority.", unique_items=True)
    rotation: Rotation
    data_refresh_rate: float = Field(15.0, ge=5, description="Sets refresh rate for games data. (Min=5.0)")
    debug: bool = Field(False, description="Enable debugging.")
    testing: bool = Field(False, description="Enabled test data.")
    
    class Config:
        title = 'CFL LED Scoreboard Config Schema'
        use_enum_values = True
