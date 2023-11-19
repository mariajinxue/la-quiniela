#!/usr/bin/env python
import logging
import argparse
from datetime import datetime

import settings
from quiniela import models, io
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score


def parse_seasons(value):
    if value == "all":
        return "all"
    seasons = []
    for chunk in value.split(","):
        if ":" in chunk:
            try:
                start, end = map(int, chunk.split(":"))
                assert start < end
            except Exception:
                raise argparse.ArgumentTypeError(f"Unexpected format for seasons {value}")
            for i in range(start, end):
                seasons.append(f"{i}-{i+1}")
        else:
            try:
                start, end = map(int, chunk.split("-"))
                assert start == end - 1
            except Exception:
                raise argparse.ArgumentTypeError(f"Unexpected format for seasons {value}")
            seasons.append(chunk)
    return seasons


parser = argparse.ArgumentParser()
task_subparser = parser.add_subparsers(help='Task to perform', dest='task')
train_parser = task_subparser.add_parser("train")
train_parser.add_argument(
    "--training_seasons",
    default="all",
    type=parse_seasons,
    help="Seasons to use for training. Write them separated with ',' or use range with ':'. "
         "For instance, '2004:2006' is the same as '2004-2005,2005-2006'. "
         "Use 'all' to train with all seasons available in database.",
)
train_parser.add_argument(
    "--model_name",
    default="my_quiniela.model",
    help="The name to save the model with.",
)
predict_parser = task_subparser.add_parser("predict")
predict_parser.add_argument(
    "season",
    help="Season to predict",
)
predict_parser.add_argument(
    "division",
    type=int,
    choices=[1, 2],
    help="Division to predict (either 1 or 2)",
)
predict_parser.add_argument(
    "matchday",
    type=int,
    help="Matchday to predict",
)
predict_parser.add_argument(
    "--model_name",
    default="my_quiniela.model",
    help="The name of the model you want to use.",
)

if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(
        filename=settings.LOGS_PATH / f"{args.task}_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.log",
        format="%(asctime)s - [%(levelname)s] - %(message)s",
        level=logging.INFO,
    )
    features = ['rank_home', 'GD_home', "W_home", 
                "Pts_home", 'rank_away', 'GD_away', 
                "W_away", "Pts_away"]
    target = "result"
    if args.task == "train":
        logging.info(f"Training LaQuiniela model with seasons {args.training_seasons}")
        model = models.QuinielaModel()
        training_data = io.df_train(args.training_seasons)
        
        X_train = training_data[features]  
        y_train = training_data[target]  
        
        model.train(X_train, y_train, args.training_seasons)
        model.save(settings.MODELS_PATH / args.model_name)
        print(f"Model succesfully trained and saved in {settings.MODELS_PATH / args.model_name}")
    if args.task == "predict":
        logging.info(f"Predicting matchday {args.matchday} in season {args.season}, division {args.division}")
        model = models.QuinielaModel.load(settings.MODELS_PATH / args.model_name)
        predict_data = io.df_test(args.season, args.division, args.matchday)
        
        X_test = predict_data[features]  
        predict_data["pred"] = model.predict(X_test)
        accuracy = accuracy_score(predict_data[target], predict_data["pred"])
        
        print(f"Matchday {args.matchday} - LaLiga - Division {args.division} - Season {args.season}")
        print(f'{"Home team":^30s}    {"Away Team":^30s}     {"Prediction":^10}  {"Result":^10}')
        print("=" * 90)
        for _, row in predict_data.iterrows():
            home_team = str(row['home_team'])
            away_team = str(row['away_team'])
            pred_value = str(row['pred'])
            result = str(row['result'])
            print(f"{home_team:^30s} vs {away_team:^30s} --> {pred_value:^10}  {result:^10}")
        print(f"Accuracy: {accuracy}")
        
        io.save_predictions(predict_data)
