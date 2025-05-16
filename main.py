from config.database import establish_connection, get_config, initialize_database
from src.etl import ETLHandler
from src.report_generation import ReportGenerator
from pathlib import Path

def main():
    # Load configuration
    config = get_config()
    db_file = Path(config["database_file"])

    reference_sql = Path(config["reference_sql"])

    # Initialize SQLite connection
    conn = establish_connection(db_file)

    # Initialize the database with reference SQL
    initialize_database(conn, reference_sql)

    # Process the CSV files
    #ETLHandler.handle_files(conn)

    ## read table
    try:
        # Create a cursor object
        cursor = conn.cursor()

        # Retrieve the names of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print(f"{'Table Name':<30} {'Row Count':<10} {'Size (bytes)':<15}")
        print("=" * 55)

        for table in tables:
            table_name = table[0]

            # Get the row count for the table
            cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\";")
            row_count = cursor.fetchone()[0]

            # Get the size of the table
            cursor.execute(f"PRAGMA table_info(\"{table_name}\");")
            column_info = cursor.fetchall()
            column_count = len(column_info)

            # Estimate size (this is a rough estimate)
            # Assuming average row size is 100 bytes (adjust as necessary)
            estimated_size = row_count * column_count * 100

            print(f"{table_name:<30} {row_count:<10} {estimated_size:<15}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

    # Generate reports
    ReportGenerator.generate_price_reconciliation_report(conn, Path("price_reconciliation_report.xlsx"))
    ReportGenerator.generate_performance_report(conn, Path("performance_report.xlsx"))

    # Close the database connection
    conn.close()
    print("ETL process completed successfully.")

if __name__ == "__main__":
    main()