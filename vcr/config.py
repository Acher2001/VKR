from dataclasses import dataclass
from environs import Env

@dataclass
class Server:
    secret_key: str

@dataclass
class Config:
    server: Server

def load_config(path=None):
    env=Env()
    env.read_env(path)

    return Config(server=Server(secret_key=env('SECRET_KEY')))
