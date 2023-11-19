from pathlib import Path

BASE_DIR = Path(__file__).parent

DATABASE_PATH = BASE_DIR / "laliga.sqlite"
DATABASE_PATH_1 = BASE_DIR / "classification.sqlite"

MODELS_PATH = BASE_DIR / "models"

LOGS_PATH = BASE_DIR / "logs"