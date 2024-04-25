from dataclasses import dataclass
from environs import Env


@dataclass
class EmployeesTest:
    auth_host: str
    login: str
    password: str


@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    tg_bot: TgBot
    emp_test: EmployeesTest


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env()
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
        ),
        emp_test=EmployeesTest(
            auth_host=env('AUTH_HOST'),
            login=env('LOGIN'),
            password=env('PASSWORD')
        )
    )
