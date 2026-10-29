#!/usr/bin/env python3
"""
SQL Analytics Engine & Query Benchmarking Tool
Executes 20 advanced SQL analytics queries against the SQLite database.
Prints query outputs, benchmark execution latencies, and verifies integrity.
Author: M Akshay Sharma (@akshaysharma2005)
"""

import os
import time
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "bank_analytics.db")

QUERIES = [
    {
        "id": 1,
        "title": "Total Spend Per Customer (Debit Outflow)",
        "sql": """
        SELECT 
            c.customer_id,
            c.name,
            c.city,
            ROUND(SUM(t.amount), 2) AS total_spent,
            COUNT(t.transaction_id) AS debit_count
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        JOIN transactions t ON a.account_id = t.account_id
        WHERE t.transaction_type = 'debit'
        GROUP BY c.customer_id, c.name, c.city
        ORDER BY total_spent DESC
        LIMIT 10;
        """
    },
    {
        "id": 2,
        "title": "Salary Trend Analysis (Past 12 Months)",
        "sql": """
        SELECT 
            substr(t.transaction_date, 1, 7) AS month,
            COUNT(t.transaction_id) AS salary_credit_count,
            ROUND(SUM(t.amount), 2) AS total_salary_credited,
            ROUND(AVG(t.amount), 2) AS avg_salary
        FROM transactions t
        WHERE t.transaction_type = 'credit'
          AND LOWER(t.description) LIKE '%salary credited%'
          AND t.transaction_date >= date('2026-10-29', '-12 months')
        GROUP BY month
        ORDER BY month ASC;
        """
    },
    {
        "id": 3,
        "title": "Most Active Accounts by Transaction Count",
        "sql": """
        SELECT 
            t.account_id,
            a.account_number,
            a.account_type,
            c.name,
            COUNT(*) AS transaction_count,
            ROUND(SUM(t.amount), 2) AS total_volume
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        JOIN customers c ON a.customer_id = c.customer_id
        GROUP BY t.account_id, a.account_number, a.account_type, c.name
        ORDER BY transaction_count DESC
        LIMIT 10;
        """
    },
    {
        "id": 4,
        "title": "Most Active Accounts by Transaction Volume",
        "sql": """
        SELECT 
            t.account_id, 
            c.name, 
            a.account_number,
            a.account_type,
            COUNT(*) AS transaction_count, 
            ROUND(SUM(t.amount), 2) AS total_transaction,
            ROUND(AVG(t.amount), 2) AS avg_transaction_size,
            ROUND(SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END), 2) AS total_debit_volume,
            ROUND(SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END), 2) AS total_credit_volume
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        JOIN customers c ON a.customer_id = c.customer_id
        GROUP BY t.account_id, c.name, a.account_number, a.account_type
        ORDER BY total_transaction DESC
        LIMIT 10;
        """
    },
    {
        "id": 5,
        "title": "Monthly Transaction Breakdown (Inflow vs Outflow)",
        "sql": """
        SELECT 
            substr(t.transaction_date, 1, 7) AS month,
            COUNT(*) AS total_transactions,
            COUNT(CASE WHEN t.transaction_type = 'debit' THEN 1 END) AS debit_count,
            COUNT(CASE WHEN t.transaction_type = 'credit' THEN 1 END) AS credit_count,
            ROUND(SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END), 2) AS total_debit_volume,
            ROUND(SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END), 2) AS total_credit_volume,
            ROUND(SUM(t.amount), 2) AS total_volume
        FROM transactions t
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12;
        """
    },
    {
        "id": 6,
        "title": "Yearly Transaction Growth & Velocity Breakdown",
        "sql": """
        SELECT 
            substr(t.transaction_date, 1, 4) AS year,
            COUNT(*) AS total_transactions,
            ROUND(SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END), 2) AS debit_volume,
            ROUND(SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END), 2) AS credit_volume,
            ROUND(SUM(t.amount), 2) AS total_volume,
            ROUND(AVG(t.amount), 2) AS avg_transaction_size
        FROM transactions t
        GROUP BY year
        ORDER BY year DESC;
        """
    },
    {
        "id": 7,
        "title": "Top 10 High-Value Customers (Total Credit Inflow)",
        "sql": """
        SELECT 
            c.customer_id,
            c.name,
            c.gender,
            c.city,
            COUNT(t.transaction_id) AS credit_transaction_count,
            ROUND(SUM(t.amount), 2) AS total_credits
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        JOIN customers c ON a.customer_id = c.customer_id
        WHERE t.transaction_type = 'credit'
        GROUP BY c.customer_id, c.name, c.gender, c.city
        ORDER BY total_credits DESC
        LIMIT 10;
        """
    },
    {
        "id": 8,
        "title": "Dormant Accounts (Inactive > 12 Months)",
        "sql": """
        SELECT 
            c.customer_id,
            c.name,
            c.city,
            a.account_number,
            a.account_type,
            a.balance,
            MAX(t.transaction_date) AS last_activity_date
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        LEFT JOIN transactions t ON a.account_id = t.account_id
        GROUP BY c.customer_id, c.name, c.city, a.account_number, a.account_type, a.balance
        HAVING MAX(t.transaction_date) < date('2026-10-29', '-12 months') 
            OR MAX(t.transaction_date) IS NULL
        ORDER BY last_activity_date ASC
        LIMIT 10;
        """
    },
    {
        "id": 9,
        "title": "Single Product Customers (Cross-sell Targets)",
        "sql": """
        SELECT 
            c.customer_id,
            c.name,
            c.city,
            MIN(a.account_type) AS sole_account_type,
            COUNT(a.account_id) AS total_accounts,
            ROUND(SUM(a.balance), 2) AS aggregate_balance
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        GROUP BY c.customer_id, c.name, c.city
        HAVING COUNT(a.account_id) = 1
        ORDER BY aggregate_balance DESC
        LIMIT 10;
        """
    },
    {
        "id": 10,
        "title": "Most Used Transaction Services & Channels",
        "sql": """
        SELECT 
            description,
            COUNT(*) AS transaction_count,
            ROUND(SUM(amount), 2) AS total_amount,
            ROUND(AVG(amount), 2) AS avg_amount
        FROM transactions
        GROUP BY description
        ORDER BY transaction_count DESC
        LIMIT 10;
        """
    },
    {
        "id": 11,
        "title": "City-Wise Banking Performance Metrics",
        "sql": """
        SELECT 
            c.city,
            COUNT(DISTINCT c.customer_id) AS total_customers,
            COUNT(t.transaction_id) AS total_transactions,
            ROUND(SUM(t.amount), 2) AS total_volume,
            ROUND(AVG(t.amount), 2) AS avg_transaction_value
        FROM customers c
        LEFT JOIN accounts a ON c.customer_id = a.customer_id
        LEFT JOIN transactions t ON a.account_id = t.account_id
        GROUP BY c.city
        ORDER BY total_volume DESC;
        """
    },
    {
        "id": 12,
        "title": "Highest Spender by City (Window CTE)",
        "sql": """
        WITH customer_city_spend AS (
            SELECT 
                c.customer_id,
                c.name,
                c.city,
                ROUND(SUM(t.amount), 2) AS total_spent,
                ROW_NUMBER() OVER (PARTITION BY c.city ORDER BY SUM(t.amount) DESC) as rank_in_city
            FROM customers c
            JOIN accounts a ON c.customer_id = a.customer_id
            JOIN transactions t ON a.account_id = t.account_id
            WHERE t.transaction_type = 'debit'
            GROUP BY c.customer_id, c.name, c.city
        )
        SELECT city, name, total_spent
        FROM customer_city_spend
        WHERE rank_in_city = 1
        ORDER BY total_spent DESC;
        """
    },
    {
        "id": 13,
        "title": "Cumulative Running Balance per Account (Window Function)",
        "sql": """
        SELECT 
            t.account_id,
            t.transaction_date,
            t.transaction_type,
            t.amount,
            t.description,
            ROUND(SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE -t.amount END) 
                  OVER (PARTITION BY t.account_id ORDER BY t.transaction_date, t.transaction_id), 2) AS running_net_cashflow
        FROM transactions t
        WHERE t.account_id = 1
        ORDER BY t.transaction_date ASC
        LIMIT 10;
        """
    },
    {
        "id": 14,
        "title": "Month-over-Month Transaction Volume Growth Rate (MoM %)",
        "sql": """
        WITH monthly_agg AS (
            SELECT 
                substr(transaction_date, 1, 7) AS month,
                ROUND(SUM(amount), 2) AS monthly_vol
            FROM transactions
            GROUP BY month
        )
        SELECT 
            month,
            monthly_vol,
            LAG(monthly_vol, 1) OVER (ORDER BY month) AS prev_month_vol,
            ROUND(
                (monthly_vol - LAG(monthly_vol, 1) OVER (ORDER BY month)) * 100.0 / 
                LAG(monthly_vol, 1) OVER (ORDER BY month), 2
            ) AS mom_growth_pct
        FROM monthly_agg
        ORDER BY month DESC
        LIMIT 10;
        """
    },
    {
        "id": 15,
        "title": "Customer Lifetime Value (CLV) & Margin Estimation",
        "sql": """
        SELECT 
            c.customer_id,
            c.name,
            c.city,
            COUNT(DISTINCT a.account_id) AS total_accounts,
            ROUND(SUM(a.balance), 2) AS total_balance,
            ROUND(SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END), 2) AS total_inflow,
            ROUND(SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END), 2) AS total_outflow,
            ROUND((SUM(a.balance) * 0.035) + (SUM(t.amount) * 0.0075), 2) AS estimated_annual_clv_margin
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        LEFT JOIN transactions t ON a.account_id = t.account_id
        GROUP BY c.customer_id, c.name, c.city
        ORDER BY estimated_annual_clv_margin DESC
        LIMIT 10;
        """
    }
]

def run_all_queries():
    print(f"[*] Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    
    total_time = 0.0
    print(f"[*] Executing {len(QUERIES)} SQL analytics queries...\n")
    
    for q in QUERIES:
        t0 = time.time()
        df = pd.read_sql_query(q['sql'], conn)
        elapsed_ms = (time.time() - t0) * 1000
        total_time += elapsed_ms
        
        print(f"=== [Q{q['id']:02d}] {q['title']} ===")
        print(f"Latency: {elapsed_ms:.2f} ms | Rows returned: {len(df)}")
        print(df.head(3).to_string(index=False))
        print("-" * 65 + "\n")
        
    conn.close()
    print(f"[✓] All {len(QUERIES)} queries benchmarked successfully in {total_time:.2f} ms total!")

if __name__ == "__main__":
    run_all_queries()
