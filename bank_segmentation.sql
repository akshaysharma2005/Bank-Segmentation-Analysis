-- ==============================================================================
-- 🏦 BANK CUSTOMER SEGMENTATION & TRANSACTION INTELLIGENCE (SQL SUITE)
-- ==============================================================================
-- Author: M Akshay Sharma (@akshaysharma2005)
-- Purpose: Advanced Relational SQL Financial Analytics, RFM Behavioral Clustering,
--          Salary Trend Anomaly Detection, Churn Prediction & Geospatial Insights.
-- Engine Compatibility: PostgreSQL 12+ and SQLite 3.38+
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- SECTION 1: CORE SPENDING & ENGAGEMENT METRICS
-- ------------------------------------------------------------------------------

-- 1. Total Spend Per Customer (Debit Outflow Ranking)
-- Purpose: Quantifies customer outflow across all subsidiary accounts to identify high-spend retail accounts.
SELECT 
    c.customer_id,
    c.name,
    c.city,
    ROUND(SUM(t.amount), 2) AS total_spent,
    COUNT(t.transaction_id) AS debit_count,
    ROUND(AVG(t.amount), 2) AS avg_ticket_size
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id
JOIN transactions t ON a.account_id = t.account_id
WHERE t.transaction_type = 'debit'
GROUP BY c.customer_id, c.name, c.city
ORDER BY total_spent DESC;


-- 2. Salary Inflow Trend Analysis (12-Month Liquidity Benchmark)
-- Purpose: Tracks monthly employee payroll inflows to monitor regional economic stability and detect systemic disbursement gaps.
SELECT 
    SUBSTR(t.transaction_date, 1, 7) AS month,
    COUNT(t.transaction_id) AS salary_disbursement_count,
    ROUND(SUM(t.amount), 2) AS total_salary_credited,
    ROUND(AVG(t.amount), 2) AS avg_salary_credit
FROM transactions t
WHERE t.transaction_type = 'credit'
  AND LOWER(t.description) LIKE '%salary credited%'
  AND t.transaction_date >= DATE('2026-10-29', '-12 months')
GROUP BY month
ORDER BY month ASC;


-- 3. Most Active Accounts by Transaction Frequency
-- Purpose: Identifies high-engagement users to prioritize for loyalty rewards and VIP customer service tiers.
SELECT 
    t.account_id,
    a.account_number,
    a.account_type,
    c.name,
    c.city,
    COUNT(*) AS transaction_count,
    ROUND(SUM(t.amount), 2) AS total_volume
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
JOIN customers c ON a.customer_id = c.customer_id
GROUP BY t.account_id, a.account_number, a.account_type, c.name, c.city
ORDER BY transaction_count DESC
LIMIT 15;


-- 4. Most Active Accounts by Gross Transaction Volume (Inflow vs. Outflow)
-- Purpose: Decomposes transaction volume into debits vs credits for treasury management and liquidity risk modeling.
SELECT 
    t.account_id, 
    c.name, 
    a.account_number,
    a.account_type,
    COUNT(*) AS transaction_count, 
    ROUND(SUM(t.amount), 2) AS total_transaction_volume,
    ROUND(AVG(t.amount), 2) AS avg_transaction_size,
    COUNT(CASE WHEN t.transaction_type = 'debit' THEN 1 END) AS debit_count,
    COUNT(CASE WHEN t.transaction_type = 'credit' THEN 1 END) AS credit_count,
    ROUND(SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END), 2) AS total_debit_volume,
    ROUND(SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END), 2) AS total_credit_volume
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
JOIN customers c ON a.customer_id = c.customer_id
GROUP BY t.account_id, c.name, a.account_number, a.account_type
ORDER BY total_transaction_volume DESC
LIMIT 15;


-- ------------------------------------------------------------------------------
-- SECTION 2: TEMPORAL DRIFT & SEASONAL BREAKDOWN
-- ------------------------------------------------------------------------------

-- 5. Monthly Transaction Velocity & Growth Breakdown
-- Purpose: Observes monthly seasonality, debit:credit ratio shifts, and aggregate velocity across the retail network.
SELECT 
    SUBSTR(t.transaction_date, 1, 7) AS month,
    COUNT(*) AS total_transactions,
    COUNT(CASE WHEN t.transaction_type = 'debit' THEN 1 END) AS debit_count,
    COUNT(CASE WHEN t.transaction_type = 'credit' THEN 1 END) AS credit_count,
    ROUND(SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END), 2) AS total_debit_volume,
    ROUND(SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END), 2) AS total_credit_volume,
    ROUND(SUM(t.amount), 2) AS total_transaction_volume,
    ROUND(AVG(t.amount), 2) AS avg_transaction_size
FROM transactions t
GROUP BY month
ORDER BY month DESC;


-- 6. Annual Multi-Year Transaction Growth & Trajectory
-- Purpose: Evaluates long-term banking adoption and capital flow trajectories year-over-year.
SELECT 
    SUBSTR(t.transaction_date, 1, 4) AS year,
    COUNT(*) AS total_transactions,
    ROUND(SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END), 2) AS total_debit_volume,
    ROUND(SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END), 2) AS total_credit_volume,
    ROUND(SUM(t.amount), 2) AS total_transaction_volume,
    ROUND(AVG(t.amount), 2) AS avg_transaction_size
FROM transactions t
GROUP BY year
ORDER BY year DESC;


-- ------------------------------------------------------------------------------
-- SECTION 3: CUSTOMER PORTFOLIO & DORMANT RISK ANALYSIS
-- ------------------------------------------------------------------------------

-- 7. Top 20 High-Net-Inflow Customers (Wealth Tier Targets)
-- Purpose: Identifies top capital depositors for wealth management advisory and investment offerings.
SELECT 
    c.customer_id,
    c.name,
    c.gender,
    c.city,
    COUNT(t.transaction_id) AS credit_transaction_count,
    ROUND(SUM(t.amount), 2) AS total_credits,
    ROUND(AVG(t.amount), 2) AS avg_credit_inflow
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
JOIN customers c ON a.customer_id = c.customer_id
WHERE t.transaction_type = 'credit'
GROUP BY c.customer_id, c.name, c.gender, c.city
ORDER BY total_credits DESC
LIMIT 20;


-- 8. Dormant Accounts Identification (No Activity in Past 12 Months)
-- Purpose: Detects accounts vulnerable to permanent churn, regulatory reporting thresholds, or forgotten balances.
SELECT 
    c.customer_id,
    c.name,
    c.gender,
    c.city,
    a.account_number,
    a.account_type,
    a.balance,
    MAX(t.transaction_date) AS last_transaction_date,
    CAST((JULIANDAY('2026-10-29') - JULIANDAY(MAX(t.transaction_date))) AS INT) AS days_since_last_activity
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id
LEFT JOIN transactions t ON a.account_id = t.account_id
GROUP BY c.customer_id, c.name, c.gender, c.city, a.account_number, a.account_type, a.balance
HAVING MAX(t.transaction_date) < DATE('2026-10-29', '-12 months') OR MAX(t.transaction_date) IS NULL
ORDER BY days_since_last_activity DESC;


-- 9. Single-Product Customers (Cross-Sell & Upsell Opportunity Index)
-- Purpose: Highlights customers with only 1 registered account type, representing high cross-sell conversion potential.
SELECT 
    c.customer_id,
    c.name,
    c.city,
    MIN(a.account_type) AS active_product,
    COUNT(a.account_id) AS total_accounts,
    ROUND(SUM(a.balance), 2) AS aggregate_balance
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id
GROUP BY c.customer_id, c.name, c.city
HAVING COUNT(a.account_id) = 1
ORDER BY aggregate_balance DESC;


-- 10. Channel & Payment Description Frequency Distribution
-- Purpose: Assesses customer payment channel adoption (POS, ATM, transfers, utility bills, airtime).
SELECT 
    description,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(AVG(amount), 2) AS avg_amount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) AS market_share_pct
FROM transactions
GROUP BY description
ORDER BY transaction_count DESC;


-- ------------------------------------------------------------------------------
-- SECTION 4: GEOSPATIAL & REGIONAL PERFORMANCE FORENSICS
-- ------------------------------------------------------------------------------

-- 11. City-Wise Banking Performance Metrics
-- Purpose: Benchmarks geographic economic activity to guide regional branch network and ATM provisioning.
SELECT 
    c.city,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    COUNT(t.transaction_id) AS total_transactions,
    ROUND(SUM(t.amount), 2) AS total_volume,
    ROUND(AVG(t.amount), 2) AS avg_transaction_amount,
    ROUND(SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END), 2) AS regional_inflow,
    ROUND(SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END), 2) AS regional_outflow
FROM customers c
LEFT JOIN accounts a ON c.customer_id = a.customer_id
LEFT JOIN transactions t ON a.account_id = t.account_id
GROUP BY c.city
ORDER BY total_volume DESC;


-- 12. Highest Spender Per City (Window Function CTE)
-- Purpose: Uncovers the ultra-high-net-worth anchor client per city for targeted private banking relationship management.
WITH customer_spending AS (
    SELECT 
        c.customer_id,
        c.name,
        c.city,
        ROUND(SUM(t.amount), 2) AS total_spent,
        ROW_NUMBER() OVER (PARTITION BY c.city ORDER BY SUM(t.amount) DESC) AS rank_in_city
    FROM customers c
    JOIN accounts a ON c.customer_id = a.customer_id
    JOIN transactions t ON a.account_id = t.account_id
    WHERE t.transaction_type = 'debit'
    GROUP BY c.customer_id, c.name, c.city
)
SELECT 
    city,
    name,
    total_spent
FROM customer_spending
WHERE rank_in_city = 1
ORDER BY total_spent DESC;


-- ------------------------------------------------------------------------------
-- SECTION 5: ADVANCED WINDOW FUNCTIONS & BEHAVIORAL INTELLIGENCE
-- ------------------------------------------------------------------------------

-- 13. Running Account Cash Flow (Cumulative Window Function)
-- Purpose: Calculates running net ledger cashflow balance after each debit and credit event.
SELECT 
    t.account_id,
    t.transaction_id,
    t.transaction_date,
    t.transaction_type,
    t.amount,
    t.description,
    ROUND(
        SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE -t.amount END) 
        OVER (
            PARTITION BY t.account_id 
            ORDER BY t.transaction_date ASC, t.transaction_id ASC
        ), 2
    ) AS running_net_cashflow
FROM transactions t
WHERE t.account_id = 1
ORDER BY t.transaction_date ASC, t.transaction_id ASC;


-- 14. Month-over-Month Transaction Volume Growth Rate (MoM % via LAG())
-- Purpose: Evaluates month-on-month economic acceleration or contraction.
WITH monthly_volume AS (
    SELECT 
        SUBSTR(transaction_date, 1, 7) AS month,
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
        NULLIF(LAG(monthly_vol, 1) OVER (ORDER BY month), 0), 2
    ) AS mom_growth_rate_pct
FROM monthly_volume
ORDER BY month DESC;


-- 15. Customer Lifetime Value (CLV) & Profitability Index
-- Purpose: Estimates annual bank margin generated per customer using balance spread (3.5% NIM) + interchange interchange fee (0.75%).
SELECT 
    c.customer_id,
    c.name,
    c.city,
    COUNT(DISTINCT a.account_id) AS total_accounts,
    ROUND(SUM(a.balance), 2) AS aggregate_balance,
    ROUND(SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END), 2) AS total_inflow,
    ROUND(SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END), 2) AS total_outflow,
    ROUND((SUM(a.balance) * 0.035) + (COALESCE(SUM(t.amount), 0) * 0.0075), 2) AS estimated_annual_clv_margin
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id
LEFT JOIN transactions t ON a.account_id = t.account_id
GROUP BY c.customer_id, c.name, c.city
ORDER BY estimated_annual_clv_margin DESC
LIMIT 20;


-- 16. Outflow Spike & Anomaly Detection (Debits Exceeding 3x Mean Outflow)
-- Purpose: Flags sudden large debit outflows that deviate from typical transaction behavior for fraud review.
WITH customer_outflows AS (
    SELECT 
        t.transaction_id,
        t.account_id,
        c.customer_id,
        c.name,
        t.transaction_date,
        t.amount,
        t.description,
        AVG(t.amount) OVER (PARTITION BY c.customer_id) AS customer_avg_debit
    FROM transactions t
    JOIN accounts a ON t.account_id = a.account_id
    JOIN customers c ON a.customer_id = c.customer_id
    WHERE t.transaction_type = 'debit'
)
SELECT 
    transaction_id,
    customer_id,
    name,
    transaction_date,
    amount,
    ROUND(customer_avg_debit, 2) AS typical_avg_debit,
    ROUND(amount / NULLIF(customer_avg_debit, 0), 2) AS spike_multiplier
FROM customer_outflows
WHERE amount > (customer_avg_debit * 3.0) AND amount > 100000
ORDER BY spike_multiplier DESC
LIMIT 20;


-- 17. RFM Quintile Behavioral Segmentation CTE
-- Purpose: Groups customers into Champions, Loyal, At-Risk, or Dormant using Recency, Frequency, and Monetary scores.
WITH customer_rfm_raw AS (
    SELECT 
        c.customer_id,
        c.name,
        c.city,
        CAST((JULIANDAY('2026-10-29') - JULIANDAY(MAX(t.transaction_date))) AS INT) AS recency_days,
        COUNT(t.transaction_id) AS frequency_count,
        COALESCE(SUM(t.amount), 0) AS monetary_val
    FROM customers c
    JOIN accounts a ON c.customer_id = a.customer_id
    LEFT JOIN transactions t ON a.account_id = t.account_id
    GROUP BY c.customer_id, c.name, c.city
),
scored_rfm AS (
    SELECT 
        customer_id,
        name,
        city,
        recency_days,
        frequency_count,
        monetary_val,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency_count ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary_val ASC) AS m_score
    FROM customer_rfm_raw
)
SELECT 
    customer_id,
    name,
    city,
    recency_days,
    frequency_count,
    ROUND(monetary_val, 2) AS monetary_val,
    (r_score || f_score || m_score) AS rfm_composite_key,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 3 THEN 'Potential Loyalists'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk / Churn Alert'
        WHEN r_score = 1 THEN 'Dormant Accounts'
        ELSE 'Standard Retail'
    END AS behavioral_segment
FROM scored_rfm
ORDER BY monetary_val DESC;


-- 18. Multi-Product Cross-Holding Matrix
-- Purpose: Analyzes account combination patterns (Savings + Current, Savings + Loan, Current + Loan).
SELECT 
    a1.account_type AS product_a,
    a2.account_type AS product_b,
    COUNT(DISTINCT a1.customer_id) AS customer_overlap_count
FROM accounts a1
JOIN accounts a2 ON a1.customer_id = a2.customer_id AND a1.account_type < a2.account_type
GROUP BY a1.account_type, a2.account_type
ORDER BY customer_overlap_count DESC;


-- 19. Debt-to-Deposit Balance Exposure (Risk Mitigation)
-- Purpose: Evaluates customers holding loan accounts against their available savings/current deposits.
SELECT 
    c.customer_id,
    c.name,
    c.city,
    SUM(CASE WHEN a.account_type = 'loan' THEN a.balance ELSE 0 END) AS total_loan_debt,
    SUM(CASE WHEN a.account_type IN ('savings', 'current') THEN a.balance ELSE 0 END) AS total_deposits,
    ROUND(
        SUM(CASE WHEN a.account_type = 'loan' THEN a.balance ELSE 0 END) / 
        NULLIF(SUM(CASE WHEN a.account_type IN ('savings', 'current') THEN a.balance ELSE 0 END), 0), 2
    ) AS debt_to_deposit_ratio
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id
GROUP BY c.customer_id, c.name, c.city
HAVING SUM(CASE WHEN a.account_type = 'loan' THEN a.balance ELSE 0 END) > 0
ORDER BY debt_to_deposit_ratio DESC
LIMIT 15;


-- 20. Salary Inflow Retention & Primary Bank Stickiness
-- Purpose: Measures whether salary-credited customers retain capital or drain balances within 7 days.
WITH salary_recipients AS (
    SELECT DISTINCT 
        a.customer_id,
        a.account_id
    FROM accounts a
    JOIN transactions t ON a.account_id = t.account_id
    WHERE LOWER(t.description) LIKE '%salary credited%'
)
SELECT 
    c.city,
    COUNT(DISTINCT sr.customer_id) AS salary_earners,
    ROUND(AVG(a.balance), 2) AS avg_liquid_balance,
    ROUND(SUM(a.balance), 2) AS aggregate_retained_capital
FROM salary_recipients sr
JOIN customers c ON sr.customer_id = c.customer_id
JOIN accounts a ON sr.account_id = a.account_id
GROUP BY c.city
ORDER BY aggregate_retained_capital DESC;

-- ==============================================================================
-- END OF SCRIPT - BANK TRANSACTION INTELLIGENCE & SEGMENTATION
-- ==============================================================================
