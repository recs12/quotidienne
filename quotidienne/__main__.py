#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import warnings

import matplotlib as mpl
warnings.filterwarnings("ignore", category=mpl.cbook.MatplotlibDeprecationWarning)
from logzero import logger
from yaspin import yaspin

from quotidienne.acronyms import mapping_with_acronyms
from quotidienne.azure import get_azure_dataset
from quotidienne.config import check_config, config_location
from quotidienne.graphs import dms
from quotidienne.spinner import sp

mpl.rc("figure", max_open_warning=0)


__VERSION__ = "0.0.7"

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

        lastYear = azure.index.get_level_values(0).year.max()
        print("lastYear : %s" %lastYear)

        azure_last_year = azure[ azure.year == lastYear ]
        lastWeek = azure_last_year.week.max()
        print("lastWeek : %s" %lastWeek)

        lastDay = azure_last_year.date_azure.max()
        realLastDay = azure_last_year.real_date.max()
        print("lastDay : %s" % realLastDay)

        secondLastDay = azure_last_year.date_azure.drop_duplicates().nlargest(2).iloc[-1]
        realSecondLastDay = azure_last_year.real_date.drop_duplicates().nlargest(2).iloc[-1]
        print("secondLastDay : %s" %realSecondLastDay)

        azureLastWeek = azure[(azure.week == lastWeek) & (azure.year == lastYear)]
        azureLastWeekIds = azureLastWeek.index.get_level_values("assigned").unique().tolist() # list of ids in the last week
        azureLastWeekIdsWithoutZero =  list(filter(lambda num: num != 0, azureLastWeekIds)) # same list but with the zero removed
        azureGroupedbyTeamMember = azureLastWeek.groupby(level="assigned")
        os.makedirs("equipe", exist_ok=True)

        with yaspin(sp, side="left") as SP:
            for _name in team.values():
                if _name in azureLastWeekIdsWithoutZero:
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
    print("version: %s" %__VERSION__)
    main()
