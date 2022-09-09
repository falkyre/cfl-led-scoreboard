from __future__ import annotations
from typing import List
from enum import Enum
from pydantic import BaseModel, Field, validator


class Rates(BaseModel):
    pregame: float = 15.0
    live: float = 15.0
    final: float = 15.0
    
    @validator('pregame', allow_reuse=True)
    @validator('live', allow_reuse=True)
    @validator('final', allow_reuse=True)
    def rotation_rates_gte_2s(cls, v):
        if not v >= 2:
            raise ValueError('Rotation rates must be 2s or greater')
        return v

class Rotation(BaseModel):
    enabled: bool = True
    only_preferred: bool = False
    rates: Rates
    while_preferred_team_live: bool = False


class ConfigModel(BaseModel):
    preferred_teams: List[str]
    rotation: Rotation
    data_refresh_rate: float = 15.0
    debug: bool = False
    testing: bool = False
    
    class Config:
        title = 'Config'
    
    @validator('data_refresh_rate')
    def data_refresh_rate_gte_5s(cls, v):
        if not v >= 5:
            raise ValueError('data_refresh_rate must be 5s or greater')
        return v
    
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
