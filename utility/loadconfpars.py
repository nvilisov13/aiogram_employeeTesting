from utility import parsdrf
from config import load_config
from datetime import datetime

config = load_config('.env')
pars_drf = parsdrf.ParsingDRF(config.emp_test.auth_host, config.emp_test.login, config.emp_test.password)


def convert_date_time(time_stamp):
    return datetime.strftime(datetime.fromtimestamp(time_stamp), "%Y-%m-%d %H:%M:%S")


def convert_date_time_out_message(datetime_str):
    return datetime.strftime(datetime.fromisoformat(datetime_str), "%d.%m.%Y %H:%M:%S")
