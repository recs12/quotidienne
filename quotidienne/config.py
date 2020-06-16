import os
import sys

import yaml
from prompt_toolkit import prompt

user_profile = os.environ.get("USERPROFILE")

users = [
    "Slimane Rechdi <recs@premiertech.com>",
    "Pinocchio <pino@premiertech.com>",
    "Mary Poppins <popm@premiertech.com>",
    "Massinissa <mass@premiertech.com>",
    "King Julien <kinj@premiertech.com>",
    "Marie Curie <curm@premiertech.com>",
]

config_location = os.path.join(user_profile, r".quotidienne\myteam.yaml")


def config_file_exists(config):
    if os.path.exists(config):
        return True
    else:
        return False


def read_config(config):
    with open(config, "r", encoding="utf-8") as f:
        yaml_content = yaml.load(f, Loader=yaml.FullLoader)
        if not yaml_content:
            raise ValueError
        else:
            return yaml_content


def create_config_file(config):
    os.makedirs(os.path.dirname(config_location), exist_ok=True)
    with open(config, "w") as f:
        data = yaml.dump(users, f)


def prompt_create_config_file():
    answer = prompt(
        "Would you like to create a config file for your team? press [y\Y]es to continue: "
    )
    if answer.lower() in ["y", "yes", "ye"]:
        return True
    else:
        return False


def check_config(_path):
    if not config_file_exists(_path):
        if prompt_create_config_file():
            create_config_file(_path)
            print(f"config file created in {_path}")
            print("You can modify the config file and rerun the macro.")
        else:
            sys.exit()
    else:
        return read_config(_path)
