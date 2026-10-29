-- ==============================================================================
-- 🏦 BANK CUSTOMER SEGMENTATION - RELATIONAL SCHEMA DEFINITION
-- ==============================================================================
-- Author: M Akshay Sharma (@akshaysharma2005)
-- Dialect: Compatible with PostgreSQL 12+ and SQLite 3.35+
-- ==============================================================================

-- 1. Customers Master Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    gender VARCHAR(1) CHECK (gender IN ('M', 'F')),
    dob DATE,
    signup_date DATE NOT NULL,
    city TEXT NOT NULL
);

-- 2. Accounts Subsidiary Table
CREATE TABLE IF NOT EXISTS accounts (
    account_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    account_number VARCHAR(12) NOT NULL UNIQUE,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('savings', 'current', 'loan')),
    open_date DATE NOT NULL,
    balance NUMERIC(14,2) DEFAULT 0.00 CHECK (balance >= 0)
);

-- 3. Transactions Ledger Table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    account_id INT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    transaction_date DATE NOT NULL,
    amount NUMERIC(14,2) NOT NULL CHECK (amount > 0),
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('debit', 'credit')),     
    description VARCHAR(100) NOT NULL
);

-- ------------------------------------------------------------------------------
-- PERFORMANCE INDEXES (Optimized for Analytical Querying & Window Functions)
-- ------------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_customers_city ON customers(city);
CREATE INDEX IF NOT EXISTS idx_accounts_customer_id ON accounts(customer_id);
CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(account_type);
CREATE INDEX IF NOT EXISTS idx_txns_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_txns_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_txns_type ON transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_txns_acc_date ON transactions(account_id, transaction_date);
