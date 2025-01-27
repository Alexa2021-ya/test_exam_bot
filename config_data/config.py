from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    database: str


@dataclass
class TgBot:
    token: str

@dataclass
class GoogleSheet:
    key: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    google_sheet: str



def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
        ),
        db=DatabaseConfig(
            database=env('DATABASE'),
        ),
        google_sheet=GoogleSheet(
            key=env('GOOGLE_SHEET_KEY')
        ),
    )
