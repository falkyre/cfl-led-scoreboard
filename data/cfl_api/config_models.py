from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field, validator


class Rates(BaseModel):
    pregame: float = Field(default=15.0, ge=2)
    live: float = Field(default=15.0, ge=2)
    final: float = Field(default=15.0, ge=2)


class Rotation(BaseModel):
    enabled: bool = True
    only_preferred: bool = False
    rates: Rates
    while_preferred_team_live: bool = False


class ConfigModel(BaseModel):
    preferred_teams: List[str]
    rotation: Rotation
    data_refresh_rate: float = Field(default=15.0, ge=5)
    debug: bool = False
    testing: bool = False
    
    class Config:
        title = 'Config'
    
    @validator('preferred_teams')
    def check_valid_teams(cls, v):
        teams_list = [
            "BC",
            "CGY",
            "EDM",
            "HAM",
            "MTL",
            "OTT",
            "SSK",
            "TOR",
            "WPG"
            ]
        for team in v:
            if not team in teams_list:
                raise ValueError(f'Team {v} is invalid')
        return v
