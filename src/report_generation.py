import pandas as pd
import sqlite3
from pathlib import Path
from config.sql_queries import PRICE_RECONCILIATION_QUERY, PERFORMANCE_REPORT_QUERY


class ReportGenerator:
    @staticmethod
    def generate_price_reconciliation_report(conn: sqlite3.Connection, output_file: Path) -> None:
        """
        Generates a price reconciliation report comparing fund prices to reference prices.

        Args:
            conn (sqlite3.Connection): The SQLite connection object.
            output_file (Path): Path to save the reconciliation report.
        """
        df = pd.read_sql_query(PRICE_RECONCILIATION_QUERY, conn)

        # Calculate price differences
        df['price_difference'] = df['fund_price'] - df['reference_price']

        # Save to Excel
        df.to_excel(output_file, index=False)
        print(f"Price reconciliation report saved to '{output_file}'.")

    @staticmethod
    def generate_performance_report(conn: sqlite3.Connection, output_file: Path) -> None:
        """
        Generates a performance report for the funds.

        Args:
            conn (sqlite3.Connection): The SQLite connection object.
            output_file (Path): Path to save the performance report.
        """
        df = pd.read_sql_query(PERFORMANCE_REPORT_QUERY, conn)

        # Calculate rate of return
        df['rate_of_return'] = (df['total_market_value'] - df['total_market_value'].shift(1) + df[
            'total_realised_pl']) / df['total_market_value'].shift(1)

        # Save to Excel
        df.to_excel(output_file, index=False)
        print(f"Performance report saved to '{output_file}'.")