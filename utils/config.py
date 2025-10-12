import pathlib as pl
import tomllib as tl
from pydantic import BaseModel

CONFIG_PATH = pl.Path(__file__).parents[1] / 'custom_config.toml'
class DatabaseConfig(BaseModel):
    url: str

class CustomConfig(BaseModel):
    database: DatabaseConfig

def init():
    with open(CONFIG_PATH, 'rb') as f:
        data = tl.load(f)
    return CustomConfig(**data)

config = init()