import pytest
from src.etl import ETLHandler

def test_extract_name_from_filename():
    assert ETLHandler.extract_name_from_filename("Applebead.28-02-2023 breakdown.csv") == "applebead"
    assert ETLHandler.extract_name_from_filename("InvalidFilename.csv") == ""