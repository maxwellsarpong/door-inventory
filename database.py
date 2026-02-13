from pathlib import Path
import platform
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_app_data_dir():
    system = platform.system()
    if system == "Windows":
        return Path.home() / "AppData" / "Roaming" / "CED"
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "CED"
    else:
        return Path.home() / ".ced"

APP_DIR = get_app_data_dir()
APP_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = APP_DIR / "ced.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)
