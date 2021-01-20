import glob

import pandas as pd
from pandas.tseries.offsets import DateOffset


def csv_parser(file_name, team, parse_dates=True):
    df = pd.read_csv(file_name, encoding="utf-8")
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


def get_azure_dataset(team):
    sprint = [csv for csv in glob.glob("*.{}".format("csv"))]
    if sprint == []:
        raise FileNotFoundError
    sprintDFs = [csv_parser(day, team) for day in sprint]
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
    azure["date_azure"] = azure.index.get_level_values(0) + DateOffset(days=-3) # azure week end in Thursday so 3 days offset.
    azure["real_date"] = azure.index.get_level_values(0) + DateOffset(days=0)
    azure.date_azure = pd.to_datetime(azure.date_azure)
    azure["week_azure"] = azure.date_azure.dt.week
    azure["task"] = (
        azure["tags"].astype(str) + "_" + azure["title"].astype(str)
    )

    # Order the columns here.
    return azure[
        [
            "year",
            "week",
            "week_azure",
            "Jour",
            "date_azure",
            "real_date",
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
