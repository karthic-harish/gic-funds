import os
import re
import pandas as pd
import sqlite3
from pathlib import Path
from pydantic import BaseModel, validator, Field
from config.database import get_config
from typing import Tuple, Optional

class FundRecord(BaseModel):
    financial_type: str = Field(..., alias='financial_type')
    symbol: str = Field(..., alias='symbol')
    security_name: str = Field(..., alias='security_name')
    sedol: Optional[str] = Field(None, alias='sedol')  # Make SEDOL optional
    isin: Optional[str] = Field(None, alias='isin')    # Make ISIN optional
    price: float = Field(..., alias='price')
    quantity: float = Field(..., alias='quantity')
    realised_pl: float = Field(..., alias='realised_pl')
    market_value: float = Field(..., alias='market_value')

    @validator('price', 'quantity', 'market_value')
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError('Must be a positive number')
        return v

class ETLHandler:
    @staticmethod
    def create_or_update_table(conn: sqlite3.Connection, table_name: str) -> None:
        """Creates or updates a table in the SQLite database based on the CSV schema."""
        print(f"Creating or updating table '{table_name}'")
        # Drop the table if it exists
        drop_table_query = f"DROP TABLE IF EXISTS \"{table_name}\";"  # Use quotes around the table name
        conn.execute(drop_table_query)

        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                financial_type TEXT,
                symbol TEXT,
                security_name TEXT,
                sedol TEXT,
                isin TEXT,
                price REAL,
                quantity REAL,
                realised_pl REAL,
                market_value REAL,
                date TEXT,  -- Add this line for the date column
                UNIQUE(symbol, date)  -- Ensure uniqueness based on symbol and date
            )
        """
        try:
            conn.execute(create_table_query)
            print(f"Table '{table_name}' created or updated successfully.")
        except Exception as e:
            print(f"Error creating or updating table '{table_name}': {e}")

    @staticmethod
    def load_csv_to_table(conn: sqlite3.Connection, table_name: str, csv_file: Path, date: str) -> None:
        """Loads data from the CSV file into the specified table."""
        print(f"Loading data from '{csv_file.name}' into table '{table_name}'")
        df = pd.read_csv(csv_file)

        # Trim whitespace from column names
        df.columns = df.columns.str.strip()
        print("DataFrame columns:", df.columns.tolist())  # Print the columns for debugging

        # Check for the presence of SEDOL or ISIN
        if 'SEDOL' not in df.columns and 'ISIN' not in df.columns:
            raise ValueError(f"Neither 'SEDOL' nor 'ISIN' column is present in the CSV file: {csv_file.name}")

        # Fill NaN values with a placeholder for SEDOL and ISIN
        if 'SEDOL' in df.columns:
            df['SEDOL'] = df['SEDOL'].fillna('')  # Assign the result back
        if 'ISIN' in df.columns:
            df['ISIN'] = df['ISIN'].fillna('')  # Assign the result back

        df = df.head(1)

        # Validate and convert each row to FundRecord
        for _, row in df.iterrows():
            try:
                # Print the entire row for debugging
                #print("Processing row:", row)

                # Create a fund record with the correct mapping
                fund_record_data = {
                    'financial_type': row.get('FINANCIAL TYPE'),
                    'symbol': row.get('SYMBOL'),
                    'security_name': row.get('SECURITY NAME'),
                    'sedol': row.get('SEDOL', None),  # Default to None if not present
                    'isin': row.get('ISIN', None),  # Default to None if not present
                    'price': row.get('PRICE'),
                    'quantity': row.get('QUANTITY'),
                    'realised_pl': row.get('REALISED P/L'),
                    'market_value': row.get('MARKET VALUE')
                }

                # Print fund_record_data for debugging
                #print("Fund Record Data:", fund_record_data)

                # Check for missing required fields
                for key in ['financial_type', 'symbol', 'security_name', 'price', 'quantity', 'realised_pl',
                            'market_value']:
                    if fund_record_data[key] is None:
                        raise ValueError(f"Missing required field: {key}")

                fund_record = FundRecord(**fund_record_data)


                # Check if the record already exists
                query = f"""
                       SELECT COUNT(*) FROM {table_name} 
                       WHERE symbol = ? AND date = ?
                   """
                existing_count = conn.execute(query, (fund_record.symbol, date)).fetchone()[0]

                if existing_count == 0:  # If the record does not exist
                    insert_query = f"""
                           INSERT INTO {table_name} (financial_type, symbol, security_name, sedol, isin, price, quantity, realised_pl, market_value, date)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       """
                    conn.execute(insert_query,
                                 (fund_record.financial_type, fund_record.symbol, fund_record.security_name,
                                  fund_record.sedol, fund_record.isin, fund_record.price,
                                  fund_record.quantity, fund_record.realised_pl,
                                  fund_record.market_value, date))
                else:
                    print(f"Record for {fund_record.symbol} on {date} already exists. Skipping.")

            except Exception as e:
                print(f"Error processing row: {row}. Error: {e}")
        conn.commit()
        print(f"Data loaded into table '{table_name}' successfully.")


    @staticmethod
    def handle_files(conn: sqlite3.Connection) -> None:
        """Processes all CSV files in the input directory by creating/updating tables and loading data into SQLite."""
        config = get_config()
        folder_path = Path(config["csv_folder"])
        print(f"Looking for CSV files in: {folder_path}")

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".csv"):
                file_path = folder_path / filename
                result = ETLHandler.extract_name_and_date_from_filename(filename)

                if not result:
                    print(f"Could not extract fund name and date from '{filename}'. Skipping file.")
                    continue

                fund_name, date = result
                table_name = fund_name  # Use the fund name as the table name

                ETLHandler.create_or_update_table(conn, table_name)
                ETLHandler.load_csv_to_table(conn, table_name, file_path, date)  # Pass the date to the load function

    @staticmethod
    def extract_name_and_date_from_filename(filename: str) -> Optional[Tuple[str, str]]:
        """Extracts the fund name and date from the filename."""
        # Match fund name and date in various formats, allowing for optional prefixes
        match = re.match(r'.*?([^.\d]+)\.?(?:(\d{2}[-_]\d{2}[-_]\d{4})|(\d{8})).*', filename)
        if match:
            fund_name = match.group(1).strip()  # Extract fund name and strip whitespace
            fund_name = re.sub(r'^(fund\s+|report-of\s+|rpt\s+|monthly\s+|details\s+|mend-report\s+)?', '', fund_name,
                               flags=re.IGNORECASE).strip()  # Remove any leading descriptors
            date = match.group(2) if match.group(2) else match.group(3)  # Get date from either group
            if date:
                # Convert date to YYYY-MM-DD format
                if '-' in date:  # If the date is in DD-MM-YYYY or DD_MM_YYYY format
                    day, month, year = date.replace('_', '-').split('-')
                    date_formatted = f"{year}-{month}-{day}"
                else:  # If the date is in YYYYMMDD format
                    date_formatted = f"{date[:4]}-{date[4:6]}-{date[6:]}"
                if 'gohen' in fund_name.lower():
                    fund_name = 'gohen'
                if 'catalysm' in fund_name.lower():
                    fund_name = 'catalysm'
                return fund_name.lower(), date_formatted  # Return fund name in lowercase and formatted date
        return None

    @staticmethod
    def execute_etl() -> None:
        """Main function to execute the ETL process."""
        config = get_config()
        db_file = Path(config["database_file"])

        # Initialize SQLite connection
        conn = establish_connection(db_file)

        # Process the files
        ETLHandler.handle_files(conn)

        conn.close()
        print("All CSV files have been processed successfully.")