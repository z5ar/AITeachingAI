import pathlib as pl
import tomllib as tl
from pydantic import BaseModel, Field
from typing import Annotated

CONFIG_PATH = pl.Path(__file__).parents[1] / 'custom_config.toml'
class DatabaseConfig(BaseModel):
    url: str

class SessionIDConfig(BaseModel):
    ttl: Annotated[int, Field(ge=0)]

class CustomConfig(BaseModel):
    database: DatabaseConfig
    sessionid: SessionIDConfig

def init():
    with open(CONFIG_PATH, 'rb') as f:
        data = tl.load(f)
    return CustomConfig(**data)

config = init()