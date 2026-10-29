import json
import sqlite3
import os

DB_PATH = "/Users/makshaysharma/Downloads/Bank-Segmentation-Analysis-main/data/bank_analytics.db"
conn = sqlite3.connect(DB_PATH)

# 1. KPIs
kpis = {
    "total_volume": "₦1.86B",
    "total_customers": 500,
    "total_accounts": 1050,
    "total_transactions": 6000,
    "active_ratio": "84.2%",
    "dormant_ratio": "15.8%",
    "avg_ticket": "₦310.2K",
    "gross_deposits": "₦2.84B"
}

# 2. Monthly Trend
cur = conn.cursor()
cur.execute("""
SELECT 
    substr(transaction_date, 1, 7) as month,
    COUNT(*) as txn_count,
    ROUND(SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) / 1000000.0, 2) as credit_vol,
    ROUND(SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) / 1000000.0, 2) as debit_vol,
    ROUND(SUM(amount) / 1000000.0, 2) as total_vol
FROM transactions
WHERE transaction_date >= '2024-11-01'
GROUP BY month
ORDER BY month ASC
""")
monthly = [{"month": r[0], "count": r[1], "credit": r[2], "debit": r[3], "total": r[4]} for r in cur.fetchall()]

# 3. Cities
cur.execute("""
SELECT 
    c.city,
    COUNT(DISTINCT c.customer_id) as customers,
    COUNT(t.transaction_id) as txns,
    ROUND(SUM(t.amount) / 1000000.0, 2) as volume,
    ROUND(AVG(t.amount), 2) as avg_val
FROM customers c
LEFT JOIN accounts a ON c.customer_id = a.customer_id
LEFT JOIN transactions t ON a.account_id = t.account_id
GROUP BY c.city
ORDER BY volume DESC
""")
cities = [{"city": r[0], "customers": r[1], "txns": r[2], "volume": r[3], "avg": r[4]} for r in cur.fetchall()]

# 4. Segments
cur.execute("""
SELECT segment, COUNT(*) as cnt, ROUND(AVG(monetary) / 1000000.0, 2) as avg_monetary
FROM customer_rfm_segments
GROUP BY segment
ORDER BY cnt DESC
""")
segments = [{"segment": r[0], "count": r[1], "avg_monetary": r[2]} for r in cur.fetchall()]

# 5. Customer Table
cur.execute("""
SELECT customer_id, name, city, gender, recency, frequency, ROUND(monetary, 2), segment, cluster, ROUND(total_balance, 2)
FROM customer_rfm_segments
ORDER BY monetary DESC
LIMIT 100
""")
customers = [
    {
        "id": r[0], "name": r[1], "city": r[2], "gender": r[3],
        "recency": r[4], "frequency": r[5], "monetary": r[6],
        "segment": r[7], "cluster": r[8], "balance": r[9]
    }
    for r in cur.fetchall()
]

# 6. Channel Usage
cur.execute("""
SELECT description, COUNT(*) as cnt, ROUND(SUM(amount) / 1000000.0, 2) as vol
FROM transactions
GROUP BY description
ORDER BY cnt DESC
LIMIT 8
""")
channels = [{"desc": r[0], "count": r[1], "vol": r[2]} for r in cur.fetchall()]

data_bundle = {
    "kpis": kpis,
    "monthly": monthly,
    "cities": cities,
    "segments": segments,
    "customers": customers,
    "channels": channels
}

out_path = "/Users/makshaysharma/Downloads/Bank-Segmentation-Analysis-main/dashboard_data.js"
with open(out_path, "w") as f:
    f.write("const BANK_DATA = " + json.dumps(data_bundle, indent=2) + ";\n")

print("Generated dashboard_data.js with size:", os.path.getsize(out_path), "bytes")
conn.close()
