import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from yaspin import yaspin


def graph_member_ids(az, azure, acronym):

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

    _today = az.index.get_level_values(0)[-1]
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


def dms(acronym, azure, azureGroupedbyTeamMember, lastDay, secondLastDay):
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
        graph_member_ids(lastDayReport, azure, acronym)

    # Weekly productivity
    progressWeekly = teammate.progress
    progressWeekly = progressWeekly.unstack(level="id", fill_value=0)
    progressWeekly["Somme avancement"] = progressWeekly.sum(axis=1)
    progressWeekly["Jour"] = progressWeekly.index.get_level_values(0).dayofweek
    progressWeekly["Jour"] = progressWeekly["Jour"].replace(
        [0, 1, 2, 3, 4, 5, 6], ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    )
    graph_week_productivity(progressWeekly, acronym)
