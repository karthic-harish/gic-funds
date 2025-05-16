import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv
import sys

'''# Get the path where create.py is located
file_path = os.path.abspath(__file__)
print(file_path)
# Get the directory where create.py is located
base_dir = os.path.dirname(file_path)
# Set project root path and add current working dir to sys path to import configs and utils
PROJECT_ROOT_PATH = os.path.dirname(os.path.dirname(base_dir))
sys.path.append(PROJECT_ROOT_PATH)
print(PROJECT_ROOT_PATH)
# Using Environment Variables
dotenv_path = os.path.join(PROJECT_ROOT_PATH, "gic-funds", "config", ".env")
print(dotenv_path)
load_dotenv(dotenv_path)'''
load_dotenv()

def establish_connection(db_file: Path) -> sqlite3.Connection:
    """Create a database connection to the SQLite database."""
    conn = sqlite3.connect(db_file)
    return conn

def initialize_database(conn: sqlite3.Connection, sql_script: str) -> None:
    """Execute SQL statements to create tables."""
    with open(sql_script, 'r') as f:
        sql_script_content = f.read()
    conn.executescript(sql_script_content)

def get_config() -> dict:
    """Get configuration settings from environment variables."""
    return {
        "database_file": os.getenv("DATABASE_FILE"),
        "reference_sql": os.getenv("REFERENCE_SQL"),
        "csv_folder": os.getenv("CSV_FOLDER"),
    }