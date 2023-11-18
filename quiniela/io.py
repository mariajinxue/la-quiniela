import sqlite3

import pandas as pd

import sys
import io
import settings
from settings import DATABASE_PATH, DATABASE_PATH_1


def load_matchday_laliga(season, division, matchday):
    with sqlite3.connect(DATABASE_PATH) as conn:
        data = pd.read_sql(f"""
            SELECT * FROM Matches
                WHERE season = '{season}'
                  AND division = {division}
                  AND matchday = {matchday}
        """, conn)
    if data.empty:
        raise ValueError("There is no matchday data for the values given")
    return data

def load_matchday_clasification(season, division, matchday):
    with sqlite3.connect(DATABASE_PATH_1) as conn:
        data = pd.read_sql(f"""
            SELECT * FROM clasification
                WHERE season = '{season}'
                  AND division = {division}
                  AND matchday = {matchday}
        """, conn)
    if data.empty:
        raise ValueError("There is no matchday data for the values given")
    return data

def load_historical_data_laliga(seasons):
    with sqlite3.connect(DATABASE_PATH) as conn:
        if seasons == "all":
            data = pd.read_sql("SELECT * FROM Matches", conn)
        else:
            data = pd.read_sql(f"""
                SELECT * FROM Matches
                    WHERE season IN {tuple(seasons)}
            """, conn)
    if data.empty:
        raise ValueError(f"No data for seasons {seasons}")
    return data

def load_historical_data_clasification(seasons):
    with sqlite3.connect(DATABASE_PATH_1) as conn:
        if seasons == "all":
            data = pd.read_sql("SELECT * FROM clasification", conn)
        else:
            data = pd.read_sql(f"""
                SELECT * FROM clasification
                    WHERE season IN {tuple(seasons)}
            """, conn)
    if data.empty:
        raise ValueError(f"No data for seasons {seasons}")
    return data

def save_predictions(predictions):
    predictions = predictions[["season", "division", "matchday", 
                               "date", "time", "home_team", 
                               "away_team", "score", "pred"]]
    with sqlite3.connect(DATABASE_PATH) as conn:
        predictions.to_sql(name="Predictions", con=conn, if_exists="append", index=False)

def add_result(matches):
    matches["result"] = None
    matches.loc[(matches["score"].str.split(":").str[0]) > (matches["score"].str.split(":").str[1]), "result"] = '1'
    matches.loc[(matches["score"].str.split(":").str[0]) == (matches["score"].str.split(":").str[1]), "result"] = 'X'
    matches.loc[(matches["score"].str.split(":").str[0]) < (matches["score"].str.split(":").str[1]), "result"] = '2'
    
    matches.dropna(subset="score", inplace=True)
    return matches

def merge_and_clean_home(matches, classification):
    df = pd.merge(matches.copy(), classification.copy(), 
                             left_on=['home_team', "season", "division", "matchday"],
                             right_on=['team', "season", "division", "matchday"])
    df.dropna(subset=["home_team"], inplace=True)
    df.drop("team", axis=1, inplace=True)

    return df

def merge_and_clean_visitor(df, classification):
    df2 = pd.merge(df.copy(), classification.copy(), 
                             left_on=['away_team', "season", "division", "matchday"],
                             right_on=['team', "season", "division", "matchday"],
                             suffixes=("_home", "_away"))
    df2.dropna(subset=["away_team"], inplace=True)
    df2.drop("team", axis=1, inplace=True)

    return df2

def df_train(seasons):   
    classification = load_historical_data_clasification(seasons)
    matches = load_historical_data_laliga(seasons)
    classification.dropna(subset="rank", inplace=True)
    matches = add_result(matches)
    
    df_train = merge_and_clean_home(matches, classification)
    df_train = merge_and_clean_visitor(df_train, classification)
    return df_train

def df_test(season, division, matchday):
    classification = load_matchday_clasification(season, division, matchday)
    matches =load_matchday_laliga(season, division, matchday)
    classification.dropna(subset="rank", inplace=True)
    matches = add_result(matches)
    
    df_test = merge_and_clean_home(matches,classification)
    df_test = merge_and_clean_visitor(df_test, classification)
    return df_test