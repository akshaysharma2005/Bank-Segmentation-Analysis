#!/usr/bin/env python3
"""
Bank Customer Segmentation & Transaction Intelligence - Synthetic Data Generator
Generates realistic multi-tier banking data across customers, accounts, and transactions.
Stores output in SQLite database and exports CSVs for direct querying and analysis.
Author: M Akshay Sharma (@akshaysharma2005)
"""

import os
import random
import sqlite3
import datetime
import pandas as pd
import numpy as np

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "bank_analytics.db")

FIRST_NAMES = [
    'Chinedu', 'Aisha', 'Tunde', 'Ngozi', 'Bola', 'Obinna', 'Fatima', 'Yakubu',
    'Emeka', 'Zainab', 'Ifeanyi', 'Uche', 'Abubakar', 'Lilian', 'Segun', 'Halima', 
    'Adesuwa', 'Kehinde', 'Mercy', 'Emmanuel', 'Oluwaseun', 'Amara', 'Babatunde',
    'Kelechi', 'Funke', 'Damilola', 'Femi', 'Blessing', 'Chioma', 'David'
]

LAST_NAMES = [
    'Okonkwo', 'Balogun', 'Adegoke', 'Nwachukwu', 'Danjuma', 'Adelaja', 'Ibrahim',
    'Umeh', 'Ogunleye', 'Abiola', 'Mohammed', 'Eze', 'Lawal', 'Obi', 'Ahmed', 'Onyeka',
    'Nwabueze', 'Ajibade', 'Suleman', 'Johnson', 'Adeyemi', 'Okafor', 'Bello', 'Aliyu'
]

CITIES = [
    'Lagos', 'Abuja', 'Port Harcourt', 'Enugu', 'Kano', 'Ibadan', 'Jos', 'Abeokuta',
    'Calabar', 'Owerri', 'Benin City', 'Kaduna'
]

CITY_WEIGHTS = [0.32, 0.22, 0.16, 0.06, 0.06, 0.05, 0.03, 0.03, 0.02, 0.02, 0.02, 0.01]

CREDIT_DESCRIPTIONS = [
    'Salary credited',
    'Bank transfer from GTBank',
    'Credit alert from Zenith',
    'Reversal of failed transaction',
    'Loan disbursement',
    'Wallet top-up',
    'Refund from vendor',
    'POS reversal',
    'Received from customer',
    'Online payment received',
    'Cash deposit'
]

DEBIT_DESCRIPTIONS = [
    'POS payment at Shoprite',
    'MTN Airtime recharge',
    'Fuel purchase at Mobil',
    'Electricity bill payment',
    'Loan EMI debit',
    'House rent payment',
    'Online purchase at Jumia',
    'Cash withdrawal from ATM',
    'Subscription payment',
    'Insurance premium debit',
    'Bank transfer to Fidelity Bank'
]

def generate_dataset(num_customers=500, num_transactions=6000):
    print(f"[*] Generating {num_customers} customers and {num_transactions} transactions...")
    
    today = datetime.date(2026, 10, 29)
    customers = []
    
    # 1. Customers
    for cid in range(1, num_customers + 1):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        name = f"{fn} {ln}"
        gender = 'M' if random.random() < 0.52 else 'F'
        
        # Age between 21 and 65
        birth_year = random.randint(1961, 2005)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        dob = datetime.date(birth_year, birth_month, birth_day).isoformat()
        
        # Signup date within last 4 years
        signup_offset = random.randint(30, 1460)
        signup_date = (today - datetime.timedelta(days=signup_offset)).isoformat()
        
        city = random.choices(CITIES, weights=CITY_WEIGHTS, k=1)[0]
        customers.append({
            'customer_id': cid,
            'name': name,
            'gender': gender,
            'dob': dob,
            'signup_date': signup_date,
            'city': city
        })
        
    df_customers = pd.DataFrame(customers)
    
    # 2. Accounts
    accounts = []
    acc_id = 1
    for c in customers:
        cid = c['customer_id']
        signup_dt = datetime.date.fromisoformat(c['signup_date'])
        
        # 75% have 2 accounts, 15% have 3 accounts, 10% have 1 account
        r = random.random()
        if r < 0.10:
            num_accs = 1
        elif r < 0.85:
            num_accs = 2
        else:
            num_accs = 3
            
        acc_types = ['savings', 'current', 'loan']
        chosen_types = random.sample(acc_types, k=num_accs)
        
        for atype in chosen_types:
            acc_num = f"{random.randint(1000000000, 9999999999)}"
            open_offset = random.randint(0, 60)
            open_date = (signup_dt + datetime.timedelta(days=open_offset)).isoformat()
            
            # Balance based on account type
            if atype == 'savings':
                bal = round(random.uniform(2000, 450000), 2)
            elif atype == 'current':
                bal = round(random.uniform(15000, 2500000), 2)
            else: # loan
                bal = round(random.uniform(50000, 1200000), 2)
                
            accounts.append({
                'account_id': acc_id,
                'customer_id': cid,
                'account_number': acc_num,
                'account_type': atype,
                'open_date': open_date,
                'balance': bal
            })
            acc_id += 1
            
    df_accounts = pd.DataFrame(accounts)
    
    # 3. Transactions
    # To simulate realistic bank behavior:
    # 70% of accounts are active (frequent txns)
    # 15% are moderate
    # 15% are dormant (no txns in last 12-18 months)
    transactions = []
    txn_id = 1
    
    account_ids = df_accounts['account_id'].tolist()
    dormant_accounts = set(random.sample(account_ids, k=int(len(account_ids) * 0.15)))
    
    # Assign monthly salaries for a subset of customers (employed segment)
    salary_customers = set(random.sample([c['customer_id'] for c in customers], k=int(len(customers) * 0.45)))
    salary_accounts = {}
    for acc in accounts:
        if acc['customer_id'] in salary_customers and acc['account_type'] in ['savings', 'current']:
            salary_accounts[acc['customer_id']] = acc['account_id']
            
    # Monthly salary dates for past 24 months
    for cid, aid in salary_accounts.items():
        base_salary = round(random.uniform(85000, 650000), 2)
        for m in range(24):
            # 25th of each month
            m_date = today - datetime.timedelta(days=m * 30 + random.randint(0, 3))
            # skip dormant accounts for recent dates
            if aid in dormant_accounts and m_date > (today - datetime.timedelta(days=380)):
                continue
            transactions.append({
                'transaction_id': txn_id,
                'account_id': aid,
                'transaction_date': m_date.isoformat(),
                'amount': base_salary,
                'transaction_type': 'credit',
                'description': 'Salary credited'
            })
            txn_id += 1
            
    # Regular daily retail transactions
    remaining_txns = num_transactions - len(transactions)
    for _ in range(remaining_txns):
        aid = random.choice(account_ids)
        is_dormant = aid in dormant_accounts
        
        if is_dormant:
            # Dormant: transactions happened between 380 and 800 days ago
            days_ago = random.randint(380, 800)
        else:
            # Active: weighted towards recent days
            days_ago = int(np.random.exponential(scale=90))
            days_ago = min(days_ago, 730)
            
        txn_date = (today - datetime.timedelta(days=days_ago)).isoformat()
        
        # Credit vs Debit: 40% credit, 60% debit
        if random.random() < 0.40:
            ttype = 'credit'
            desc = random.choice(CREDIT_DESCRIPTIONS)
            amt = round(random.uniform(1500, 320000), 2)
        else:
            ttype = 'debit'
            desc = random.choice(DEBIT_DESCRIPTIONS)
            amt = round(random.uniform(500, 185000), 2)
            
        transactions.append({
            'transaction_id': txn_id,
            'account_id': aid,
            'transaction_date': txn_date,
            'amount': amt,
            'transaction_type': ttype,
            'description': desc
        })
        txn_id += 1
        
    df_txns = pd.DataFrame(transactions)
    df_txns.sort_values(by=['transaction_date'], ascending=False, inplace=True)
    df_txns['transaction_id'] = range(1, len(df_txns) + 1)
    
    # Export CSVs
    print(f"[*] Exporting CSVs to {DATA_DIR}...")
    df_customers.to_csv(os.path.join(DATA_DIR, "customers.csv"), index=False)
    df_accounts.to_csv(os.path.join(DATA_DIR, "accounts.csv"), index=False)
    df_txns.to_csv(os.path.join(DATA_DIR, "transactions.csv"), index=False)
    
    # Store in SQLite DB
    print(f"[*] Saving SQLite database to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    
    # Enable schema constraints and indices
    cur = conn.cursor()
    cur.executescript("""
    DROP TABLE IF EXISTS transactions;
    DROP TABLE IF EXISTS accounts;
    DROP TABLE IF EXISTS customers;

    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        gender TEXT CHECK(gender IN ('M', 'F')),
        dob TEXT,
        signup_date TEXT NOT NULL,
        city TEXT
    );

    CREATE TABLE accounts (
        account_id INTEGER PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(customer_id),
        account_number TEXT UNIQUE,
        account_type TEXT CHECK(account_type IN ('savings', 'current', 'loan')),
        open_date TEXT NOT NULL,
        balance NUMERIC(12,2) DEFAULT 0
    );

    CREATE TABLE transactions (
        transaction_id INTEGER PRIMARY KEY,
        account_id INTEGER REFERENCES accounts(account_id),
        transaction_date TEXT NOT NULL,
        amount NUMERIC(12,2) NOT NULL,
        transaction_type TEXT CHECK(transaction_type IN ('debit', 'credit')),
        description TEXT
    );

    CREATE INDEX idx_customers_city ON customers(city);
    CREATE INDEX idx_accounts_customer ON accounts(customer_id);
    CREATE INDEX idx_txns_account ON transactions(account_id);
    CREATE INDEX idx_txns_date ON transactions(transaction_date);
    CREATE INDEX idx_txns_type ON transactions(transaction_type);
    """)
    
    df_customers.to_sql('customers', conn, if_exists='append', index=False)
    df_accounts.to_sql('accounts', conn, if_exists='append', index=False)
    df_txns.to_sql('transactions', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()
    print(f"[✓] Data generation completed successfully! Total Txns: {len(df_txns):,}")
    return df_customers, df_accounts, df_txns

if __name__ == "__main__":
    generate_dataset()
