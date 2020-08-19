#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import warnings

import matplotlib as mpl
warnings.filterwarnings("ignore", category=mpl.cbook.MatplotlibDeprecationWarning)
from logzero import logger
# TODO: set a logging level
from yaspin import yaspin

from quotidienne.acronyms import mapping_with_acronyms
from quotidienne.azure import get_azure_dataset
from quotidienne.config import check_config, config_location
from quotidienne.graphs import dms
from quotidienne.spinner import sp

mpl.rc("figure", max_open_warning=0)


__VERSION__ = "0.0.2"

def display(team):
    print("\n")
    for id in team:
        print(f"* {id}")


def prompt_confirmation():
    answer = input("Proceed ([y]/n) ?:  ")
    if answer.lower() in ["yes", "y"]:
        pass
    else:
        print("Process has stopped.")


def prompt_confirmation():
    answer = input("\nWould you like to process with this team? [Y/y]es:  ")
    if answer.lower() in ["yes", "y"]:
        pass
    else:
        print("Process has stopped.")
        sys.exit()


def main():
    try:
        team_listing_from_config = check_config(config_location)
        display(team_listing_from_config)
        team = mapping_with_acronyms(team_listing_from_config)
        prompt_confirmation()

        azure = get_azure_dataset(team)
        # Get the last week of the total dataset
        lastDay = azure.date_azure.max()
        secondLastDay = azure.date_azure.drop_duplicates().nlargest(2).iloc[-1]
        lastWeek = azure.week_azure.max()
        lastYear = azure.index.get_level_values(0).year.max()
        azureLastWeek = azure[(azure.week_azure == lastWeek) & (azure.year == lastYear)]
        azureLastWeekIds = azureLastWeek.index.get_level_values("assigned").unique().tolist() # list of ids in the last week
        azureGroupedbyTeamMember = azureLastWeek.groupby(level="assigned")
        os.makedirs("equipe", exist_ok=True)

        with yaspin(sp, side="left") as SP:
            for _name in team.values():
                if _name in azureLastWeekIds:
                    dms(_name, azure, azureGroupedbyTeamMember, lastDay, secondLastDay)
                    SP.write(f"> {_name}\t: graphs created.")
        print("\nProcess completed.")

    except FileNotFoundError:
        logger.error("No files csv found")

    except Exception as e:
        logger.error(e.args)

    else:
        pass

    finally:
        input("\nPress any key to exit...")
        sys.exit()


if __name__ == "__main__":
    main()
