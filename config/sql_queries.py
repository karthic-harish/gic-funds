# SQL Queries for Performance and Price Reconciliation

# Query to get fund prices and reference prices for reconciliation
PRICE_RECONCILIATION_QUERY = """
SELECT 
    f.symbol,
    f.price AS fund_price,
    r.price AS reference_price,
    f.date
FROM 
    (SELECT symbol, price, date FROM applebead) f
LEFT JOIN 
    (SELECT symbol, price, date FROM equity_prices) r
ON f.symbol = r.symbol AND f.date = r.date
WHERE f.price IS NOT NULL
"""

# Query to calculate total market value and realized P/L for performance report
PERFORMANCE_REPORT_QUERY = """
SELECT 
    date,
    SUM(market_value) AS total_market_value,
    SUM(realised_pl) AS total_realised_pl
FROM 
    applebead
GROUP BY 
    date
"""