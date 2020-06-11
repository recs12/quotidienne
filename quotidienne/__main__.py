#!/usr/bin/env python
# coding: utf-8

import glob
import os, sys
from logzero import logger

import matplotlib as mpl
mpl.rc("figure", max_open_warning=0)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pandas.tseries.offsets import DateOffset
from yaspin import yaspin

from quotidienne import team
from quotidienne.spinner import sp


def prompt_confirmation():
    "ask user to resume the program"
    answer = input("Proceed ([y]/n) ?:  ")
    if answer.lower() in ["yes", "y"]:
        pass
    else:
        print("Process has stopped.")
        sys.exit()


def csv_parser(file_name, parse_dates=True):
    df = pd.read_csv(file_name)
    df = df.rename(
        columns={
            "State": "state",
            "ID": "id",
            "Title": "title",
            "Assigned To": "assigned",
            "Tags": "tags",
            "Original Estimate": "estimate",
            "Completed Work": "completed",
            "Remaining Work": "remaining",
        }
    )
    df.assigned = df.assigned.map(team)
    df = df.fillna(0)
    df["date"] = file_name.split(".")[0]
    return df


def graph_member_ids(az, acronym):

    # seaborn
    sns.set()
    sns.set_context("poster")

    # Initialize the matplotlib figure
    f, ax = plt.subplots(figsize=(10, len(az) + 1))

    _today = azure.index.get_level_values(0)[-1]
    ax.set_title(f"{acronym}\n{_today.strftime('%d %B %Y')}\n")

    # Plot the azure remaining
    sns.set_color_codes("bright")
    sns.barplot(
        x=az["completed"] + az["remaining"],
        y="task",
        data=az,
        label="remaining",
        color="b",
    )

    # Plot the azure progress
    sns.set_color_codes("bright")
    sns.barplot(x=az["completed"], y="task", data=az, label="progress", color="g")

    # Plot the azure completed
    sns.set_color_codes("bright")
    sns.barplot(
        x=az["completed"] - az["progress"],  # -az['progress2'],
        y="task",
        data=az,
        label="completed",
        color="y",
    )

    # Plot the azure estimated
    sns.set_color_codes("bright")
    sns.pointplot(
        x="estimated",
        y="task",
        data=az,
        label="estimated",
        color="black",
        join=False,
        markers="D",
        scale=0.75,
    )

    plt.setp(ax.lines, zorder=1)
    plt.setp(ax.collections, zorder=3, label="")

    # Add a legend and informative axis label
    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0, frameon=False)
    ax.set(ylabel="", xlabel="Heures")

    sns.despine(left=True, bottom=True)
    plt.savefig(f"equipe\{acronym}_2.png", bbox_inches="tight")


def graph_week_productivity(az, acronym):

    # seaborn
    sns.set()
    sns.set_style("whitegrid")
    sns.set_context("poster")

    # Initialize the matplotlib figure
    f, ax = plt.subplots(figsize=(10, 5))

    _today = azure.index.get_level_values(0)[-1]
    ax.set_title(f"{acronym}\n")

    # Plot the azure progress
    sns.set_color_codes("bright")
    sns.barplot(x="Jour", y="Somme avancement", data=az, color="g")

    # Add a legend and informative axis label
    ax.set(xlim=(0.5, 5), ylabel="Heures", xlabel="")
    ax.set(ylim=(0, 10))

    # set individual bar lables using above list
    total = 6.4

    # set individual bar lables using above list
    for i in ax.patches:
        ax.text(
            i.get_x() + 0.2,
            0,
            str(round((i.get_height() / total) * 100, 0)) + "%",
            fontsize=15,
            color="black",
        )

    sns.despine(left=True, bottom=True)

    plt.savefig(f"equipe\{acronym}_1.png", bbox_inches="tight")


def dms(acronym):
    dataGrouped = {member: group for member, group in azureGroupedbyTeamMember}

    teammate = dataGrouped[acronym][
        [
            "title",
            "state",
            "tags",
            "estimate",
            "completed",
            "remaining",
            "task",
            "progress",
            "date_azure",
        ]
    ]
    teammate_lastday = teammate[teammate["date_azure"] == lastDay]
    teammate_secondLastDay = teammate[teammate["date_azure"] == secondLastDay]
    teammate = teammate.swaplevel("assigned", "id")
    teammate = teammate.droplevel(level="assigned")
    teammate = teammate.unstack(level="date").stack()
    teammate = teammate.sort_values("date", ascending=True)

    # Get the titles
    _tasks = [
        pd.DataFrame(group).iloc[-1].at["task"]
        for id_number, group in teammate_lastday.groupby(level="id")
    ]

    # Get the states
    _states = [
        pd.DataFrame(group).iloc[-1].at["state"]
        for id_number, group in teammate_lastday.groupby(level="id")
    ]

    # Get the estimated
    _estimated = np.array(
        [
            pd.DataFrame(group).iloc[-1].at["estimate"]
            for id_number, group in teammate_lastday.groupby(level="id")
        ]
    )

    # Get the remaining
    _remaining = np.array(
        [
            pd.DataFrame(group).iloc[-1].at["remaining"]
            for id_number, group in teammate_lastday.groupby(level="id")
        ]
    )

    # Get the completed
    _completed = np.array(
        [
            pd.DataFrame(group).iloc[-1].at["completed"]
            for id_number, group in teammate_lastday.groupby(level="id")
        ]
    )

    # Get the progress
    _progress = np.array(
        [
            pd.DataFrame(group).iloc[-1].at["progress"]
            for id_number, group in teammate_lastday.groupby(level="id")
        ]
    )

    lastDayReport = pd.DataFrame(
        {
            "state": _states,
            "task": _tasks,
            "estimated": _estimated,
            "remaining": _remaining,
            "completed": _completed,
            "progress": _progress,
            # "progress2" : _progress2,
        }
    )
    lastDayReport = lastDayReport.sort_values("task", ascending=True)

    lastDayReport = lastDayReport[
        ~(lastDayReport["remaining"] == 0) | ~(lastDayReport["progress"] == 0)
    ]
    if lastDayReport.empty == False:
        graph_member_ids(lastDayReport, acronym)

    # Weekly productivity
    progressWeekly = teammate.progress
    progressWeekly = progressWeekly.unstack(level="id", fill_value=0)
    progressWeekly["Somme avancement"] = progressWeekly.sum(axis=1)
    progressWeekly["Jour"] = progressWeekly.index.get_level_values(0).dayofweek
    progressWeekly["Jour"] = progressWeekly["Jour"].replace(
        [0, 1, 2, 3, 4, 5, 6], ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    )
    graph_week_productivity(progressWeekly, acronym)


def main():
    try:
        print("Please wait...")

        sprint = [csv for csv in glob.glob("*.{}".format("csv"))]
        sprintDFs = [csv_parser(day) for day in sprint]
        azure = pd.concat(sprintDFs, sort=True)
        azure = azure.sort_values(["id", "date"], ascending=[True, True])

        # Sélectionner les tâches qui n'ont qu'une seule entrée (elles peuvent causer des progress erronés)
        single_ids = azure["id"].value_counts().reset_index()
        single_ids.columns = ["ids", "count"]
        single_ids = single_ids.loc[single_ids["count"] == 1]
        single_ids = single_ids["ids"].tolist()
        azure_single_ids = azure[azure["id"].isin(single_ids)]
        azure_single_ids = azure_single_ids[(azure_single_ids.completed > 0)]
        azure_single_ids = azure_single_ids.sort_values(["date", "id"])

        # azure_single_ids = azure_single_ids[azure_single_ids.date > '2020-03-31']
        azure["progress"] = azure.groupby("id")["completed"].diff()
        azure.progress = azure.progress.fillna(azure.completed)
        azure.date = pd.to_datetime(azure.date)
        azure = azure.set_index(["date", "assigned", "id"])
        azure["year"] = azure.index.get_level_values(0).year
        azure["Jour"] = azure.index.get_level_values(0).dayofweek
        azure["Jour"] = azure["Jour"].replace(
            [0, 1, 2, 3, 4, 5, 6],
            ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
        )
        azure["week"] = azure.index.get_level_values(0).week
        azure["date_azure"] = azure.index.get_level_values(0) + DateOffset(days=-3)
        azure.date_azure = pd.to_datetime(azure.date_azure)
        azure["week_azure"] = azure.date_azure.dt.week
        azure["task"] = azure["tags"].astype(str) + "_" + azure["title"].astype(str)

        # Impression des données avec une seule entrée dans le fichier
        azure_single_ids

        # Order the columns here.
        azure = azure[
            [
                "year",
                "week",
                "week_azure",
                "Jour",
                "date_azure",
                "tags",
                "title",
                "state",
                "estimate",
                "completed",
                "remaining",
                "task",
                "progress",
            ]
        ]

        # Get the last week of the total dataset
        lastDay = azure.date_azure.max()
        secondLastDay = azure.date_azure.drop_duplicates().nlargest(2).iloc[-1]
        lastWeek = azure.week_azure.max()
        lastYear = azure.index.get_level_values(0).year.max()
        azureLastWeek = azure[(azure.week_azure == lastWeek) & (azure.year == lastYear)]
        azureGroupedbyTeamMember = azureLastWeek.groupby(level="assigned")

    except Exception as e:
        pass

    else:
        os.makedirs('equipe', exist_ok=True)
        with yaspin(sp, side="right", text="Creating reports..."):
            for _name in team.values():
                dms(_name)
                logger.debug(f"{_name}: graphs created.")
        print("Process successfully completed.")

    finally:
        print("Press any key to exit...")
        sys.exit()


if __name__ == "__main__":
    main()

