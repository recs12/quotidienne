import os
import sys
import pandas as pd

user_profile = os.environ.get("USERPROFILE")

users = [
    "Slimane Rechdi <recs@premiertech.com>",
    "Pinocchio <pino@premiertech.com>",
    "Mary Poppins <popm@premiertech.com>",
    "Massinissa <mass@premiertech.com>",
    "King Julien <kinj@premiertech.com>",
    "Marie Curie <curm@premiertech.com>",
]

config_location = os.path.join(user_profile, r".quotidienne\myteam.csv")


def config_file_exists(config):
    if os.path.exists(config):
        return True
    return False


def read_config(config):
    """read the csv file in the .quotidenne folder
    and return a list of teammembers.
    """
    df = pd.read_csv(config, header=None)
    return df[0].tolist()


def create_config_file(config):
    os.makedirs(os.path.dirname(config_location), exist_ok=True)
    team = pd.DataFrame(users)
    team.to_csv(config, header=False, index=False)


def prompt_create_config_file():
    answer = input(
        """Would you like to create a config file for your team? press [y/Y]es to continue: """
    )
    if answer.lower() in ["y", "yes", "ye"]:
        return True
    else:
        print("Process canceled")
        sys.exit()


def check_config(_path):
    if not config_file_exists(_path):
        prompt_create_config_file()
        create_config_file(_path)
        print(f"config file created in {_path}")
        print("You can modify the config file and rerun the macro.")
        sys.exit()
    else:
        return read_config(_path)
