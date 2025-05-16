import pytest
import sqlite3
from pathlib import Path
from config.database import establish_connection, initialize_database
from src.report_generation import ReportGenerator


@pytest.fixture
def db_connection():
    db_file = Path("test_database.db")
    conn = establish_connection(db_file)
    yield conn
    conn.close()
    db_file.unlink()  # Remove the test database file after tests


def test_generate_price_reconciliation_report(db_connection):
    # Setup test data
    initialize_database(db_connection, "path/to/your/test_sql_script.sql")  # Use a test SQL script
    # Insert test data into the database for price reconciliation

    output_file = Path("test_price_reconciliation_report.xlsx")
    ReportGenerator.generate_price_reconciliation_report(db_connection, output_file)

    # Check if the output file is created
    assert output_file.exists()

    # Clean up
    output_file.unlink()


def test_generate_performance_report(db_connection):
    # Setup test data
    initialize_database(db_connection, "path/to/your/test_sql_script.sql")  # Use a test SQL script
    # Insert test data into the database for performance report

    output_file = Path("test_performance_report.xlsx")
    ReportGenerator.generate_performance_report(db_connection, output_file)

    # Check if the output file is created
    assert output_file.exists()

    # Clean up
    output_file.unlink()