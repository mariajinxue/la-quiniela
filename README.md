## LaQuiniela of LaLiga

Team members: María Jinxue García-Pantaleón Tarifa 1689933 - Juan Bendito Barrios - Antonio Pereira De la Huerga 1654167

This repo contains the skeleton for you to build your first ML project. Use the data in ```laliga.sqlite``` to build a ML model that predicts the outcome of a matchday in LaLiga (Spanish Football League).

It also contains a PDF with some exercises to practice your Python skills as a Data Scientist.

### Repository structure

```
quiniela/
  ├─── analysis/				# Jupyter Notebooks used to explore the data
  │          ...
  ├─── logs/					# Logs of the program are written
  │          ...
  ├─── models/					# The place were trained models are stored
  │          ...
  ├─── quiniela/				# Main Python package
  │          ...
  ├─── reports/					# The place to save HTML / CSV / Excel reports
  │          ...
  ├─── .gitignore
  ├─── classification.sqlite   # Database of exercise 10
  ├─── cli.py					# Main executable. Entrypoint for CLI
  ├─── laliga.sqlite			# The database
  ├─── README.md
  ├─── requirements.txt			# List of libraries needed to run the project
  └─── settings.py				# General parameters of the program
```

### How to run it

Once you've installed dependences (```pip install -r requirements.txt```):

```console
(venv) mariajinxue@MariajinxuePC:/home/la-quiniela-main$ python cli.py train --training_seasons 2000:2010
Model succesfully trained and saved in /home/la-quiniela-main/models/my_quiniela.model
(venv) mariajinxue@MariajinxuePC:/home/la-quiniela-main$ python cli.py predict 2021-2022 1 3
Matchday 3 - LaLiga - Division 1 - Season 2021-2022
          Home team                         Away Team                Prediction    Result  
==========================================================================================
         RCD Mallorca          vs            Espanyol            -->     1           1     
           Valencia            vs             Alavés             -->     1           1     
        Celta de Vigo          vs            Athletic            -->     X           2     
        Real Sociedad          vs            Levante             -->     1           1     
           Elche CF            vs           Sevilla FC           -->     X           X     
          Real Betis           vs          Real Madrid           -->     2           2     
          Barcelona            vs             Getafe             -->     1           1     
           Cádiz CF            vs           CA Osasuna           -->     X           2     
        Rayo Vallecano         vs           Granada CF           -->     1           1     
       Atlético Madrid         vs           Villarreal           -->     X           X     
Accuracy: 0.8
```

Here, we call ```train``` to train the model using seasons from 2010 to 2020, and then we perfom a prediction of 3rd matchday of 2021-2022 season at 1st Division using ```predict```. We print both, the predictions and the real results. Also we print the accuracy of this prediction.

Check out options on ```train``` and ```predict``` using ```-h``` option.

Warning : The model cannot predict the results of matches that have  not been played yet. For instance, 
```console
(venv) mariajinxue@MariajinxuePC:/home/la-quiniela-main$ python cli.py predict 2021-2022 1 4
```
cannot be execute.


### ModelAnalysis.ipynb

In ```analysis/``` folder there is a Jupyter notebook called ```ModelAnalysis.ipynb``` which contains the training and evaluation of the final model. If it is neccesary you must set your path to the main folder, in the first code cell of the notebook:
```first cell
import sys
sys.path.append('/home/la-quiniela-main/') # modify this if neccesary
```

 Also, this notebook has been exported to HTML and placed it in ```reports/``` folder.


### Data

The data is provided as two SQLite3 databases that is inside the ZIP file. 
The database ```laliga.sqlite``` contains the following tables:

   * ```Matches```: All the matches played between seasons 1928-1929 and 2021-2022 with the date and score. Columns are ```season```,	```division```, ```matchday```, ```date```, ```time```, ```home_team```, ```away_team```, ```score```. Have in mind there is no time information for many of them and also that it contains matches still not played from current season.
   * ```Predictions```: The table for you to insert your predictions. It is initially empty. Columns are ```season```, ```division```, ```matchday```, ```date```,```time```,```home_team```, ```away_team```,```score```, ```pred```.

The data source is [Transfermarkt](https://www.transfermarkt.com/), and it was scraped using Python's library BeautifulSoup4.

The database ```classification.sqlite``` contains the one table:

   * ```classification```: All the matches played between seasons 1928-1929 and 2021-2022 with the date and score. Columns are ```season```,	```division```, ```rank```, ```team```, ```matchday```, ```GF```, ```GA```, ```GD```, ```W```, ```L```, ```T```, ```Pts```, ```last_5```. It contains matches still not played from current season.



