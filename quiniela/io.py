import sqlite3

import pandas as pd

import sys
import io
import settings
from settings import DATABASE_PATH, DATABASE_PATH_1
from sklearn.preprocessing import LabelEncoder


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

def clean_matches():
    # function to clean the data from laliga.sqlite
    df = load_historical_data_laliga("all") 
    
    df["result"] = None
    df.loc[(df["score"].str.split(":").str[0]) > (df["score"].str.split(":").str[1]), "result"] = '1'
    df.loc[(df["score"].str.split(":").str[0]) == (df["score"].str.split(":").str[1]), "result"] = 'X'
    df.loc[(df["score"].str.split(":").str[0]) < (df["score"].str.split(":").str[1]), "result"] = '2'
    
    df.dropna(subset="score", inplace=True)
    return df

def merge_and_clean_home(df_games, df_teams):
    # Copiar el DataFrame para evitar modificar el original
    df = pd.merge(df_games.copy(), df_teams.copy(), 
                             left_on=['home_team', "season", "division", "matchday"],
                             right_on=['team', "season", "division", "matchday"])

    # Eliminar filas con valores nulos en la columna 'home_team'
    df.dropna(subset=["home_team"], inplace=True)
    df.drop("team", axis=1, inplace=True)

    return df

def merge_and_clean_visitor(df, df_teams):
    # Copiar el DataFrame para evitar modificar el original
    df2 = pd.merge(df.copy(), df_teams.copy(), 
                             left_on=['away_team', "season", "division", "matchday"],
                             right_on=['team', "season", "division", "matchday"],
                             suffixes=("_home", "_away"))

    # Eliminar filas con valores nulos en la columna 'home_team'
    df2.dropna(subset=["away_team"], inplace=True)
    df2.drop("team", axis=1, inplace=True)

    return df2

def select_season_train(seasons, df):
    df_train = df.copy()
    df_train["season"] = df_train["season"].astype(str)
    
    if "," in seasons:
        first_season = seasons.split(",")[0].split("-")[0]
        last_season = seasons.split(",")[-1].split("-")[1]
    else:
        first_season = seasons[0].split("-")[0]
        last_season = seasons[0].split("-")[1]
    
    df_train = df_train.loc[(df_train["season"].str.split("-").str[0] >= first_season) &
                        (df_train["season"].str.split("-").str[1] <= last_season)]
    return df_train

def select_data(df, season, division, matchday):
    df_test = df[(df["season"] == season) & 
                (df["division"] == division) & 
                (df["matchday"] == matchday)]
    return df_test

def df_train(seasons):
    # Function to create the data frame to train given certain seasons
    
    if seasons=="all":
        df_teams = load_historical_data_clasification(seasons)
        df_teams.dropna(subset="rank", inplace=True)
        df_games = clean_matches()
        
        df_train = merge_and_clean_home(df_games, df_teams)
        df_train = merge_and_clean_visitor(df_train, df_teams)
    else:
        df_teams = load_historical_data_clasification(seasons)
        df_teams.dropna(subset="rank", inplace=True)
        df_games = clean_matches()

        df_teams_train = select_season_train(seasons, df_teams)
        df_games_train = select_season_train(seasons, df_games)   
        
        df_train = merge_and_clean_home(df_games_train, df_teams_train)
        df_train = merge_and_clean_visitor(df_train, df_teams)
    return df_train

def df_test(season, division, matchday):
    df_teams = load_historical_data_clasification("all")
    df_games = clean_matches()
    
    df_teams_test = select_data(df_teams, season, division, matchday)
    df_games_test = select_data(df_games, season, division, matchday)
    
    df_test = merge_and_clean_home(df_games_test,df_teams_test)
    df_test = merge_and_clean_visitor(df_test, df_teams_test)
    return df_test