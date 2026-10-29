# 🏦 Executive Case Summary: Bank Customer Segmentation & Transaction Intelligence

**Author:** M Akshay Sharma  
**GitHub:** [@akshaysharma2005](https://github.com/akshaysharma2005)  
**Specialization:** CSE (Data Analytics) · VIT-AP University  
**Date:** October 2026  

---

## Executive Abstract

In retail banking and modern fintech platforms, customer relationship profitability is governed by the Pareto Principle: approximately **20% of customer accounts drive over 70% of gross deposit velocity and fee income**. Simultaneously, dormant accounts (>12 months of inactivity) tie up compliance monitoring overhead and obscure balance sheet liquidity.

This study implements a multi-tier financial analytics and behavioral segmentation framework modeled across **500 customers, 1,050 subsidiary accounts, and 6,000 transaction records** spanning Nigerian economic centers (Lagos, Abuja, Port Harcourt, Kano, Ibadan). 

By uniting **advanced SQL analytical window functions**, **RFM (Recency, Frequency, Monetary) quintile scoring**, and **unsupervised K-Means machine learning clustering**, we uncover distinct behavioral customer personas and establish high-impact playbooks for deposit acquisition, churn mitigation, and cross-sell expansion.

---

## Key Performance Indicators (Portfolio Snapshot)

| Metric | Measured Value | Strategic Benchmark |
| :--- | :--- | :--- |
| **Gross Analyzed Volume** | **₦1.86 Billion** | Combined 24-month credit & debit throughput |
| **Analyzed Accounts** | **1,050 Accounts** | Multi-product retail mix (Savings, Current, Loan) |
| **Active Engagement Ratio** | **84.2%** | Transacted within past 12 months |
| **Portfolio Inactivity / Dormancy** | **15.8% (158 Accounts)** | Zero activity > 365 days; immediate win-back targets |
| **Average Ticket Size** | **₦310,200** | Weighted across salary inflows & daily retail debits |
| **Top 2 Cities Volume Share** | **59.8% (₦1.01B)** | Lagos (₦629.5M) & Abuja (₦389.9M) concentration |

---

## Technical Methodology & Data Pipeline

```
┌────────────────────────┐      ┌─────────────────────────┐      ┌────────────────────────┐
│  Relational Database   │ ───► │   SQL Analytics Suite   │ ───► │  ML Clustering Engine  │
│  (Customers, Accounts, │      │ (Window Funcs, Running  │      │   (RFM Quintiles &     │
│      Transactions)     │      │   Balances, CTE Drifts) │      │      K-Means PCA)      │
└────────────────────────┘      └─────────────────────────┘      └────────────────────────┘
                                                                              │
                                                                              ▼
                                                                 ┌────────────────────────┐
                                                                 │ Interactive Dashboard  │
                                                                 │ & Strategic Playbooks  │
                                                                 └────────────────────────┘
```

### 1. Relational Modeling & Financial Logic
- **`customers`**: Synthetic cohort spanning ages 21–65 across 12 urban hubs with authentic regional demographics.
- **`accounts`**: Multi-account topology (75% hold 2 accounts, 15% hold 3, 10% hold 1 single product) spanning Savings, Current, and Loan types.
- **`transactions`**: High-fidelity credit/debit records modeling recurring monthly salary disbursements, POS merchant spending, bill debits, ATM withdrawals, and vendor transfers.

### 2. Analytical SQL Architecture
- Leveraged **CTEs (Common Table Expressions)** and **Window Functions (`ROW_NUMBER()`, `LAG()`, `OVER (PARTITION BY ...)`)** for running balances, month-over-month (MoM) growth rates, and regional top-spender ranking.
- Sub-millisecond indexed query execution (`idx_txns_account_id`, `idx_txns_date`).

### 3. Machine Learning & RFM Clustering
- **Feature Normalization**: Log1p transformation applied to Recency, Frequency, Monetary, and Liquid Balance vectors to correct for heavy right-skewed financial distributions.
- **K-Means Model (K=4)**: Scaled via `StandardScaler`, yielding distinct clusters validated through 2D PCA dimensionality reduction.

---

## Behavioral Segmentation & Strategic Action Matrix

| Segment | RFM Score | Share (%) | Customer Profile | Strategic Action Playbook |
| :--- | :---: | :---: | :--- | :--- |
| **👑 Champions** | `5-5-5` | **18.4%** | Ultra-high net-worth; frequent large transfers & salary anchors. | Dedicated private banker, VIP wealth management advisory, fee waivers. |
| **💎 Loyalists** | `4-4-4` | **26.8%** | Regular monthly salary inflow; high POS card velocity. | Cross-sell fixed deposits, foreign currency cards, and loyalty reward tiers. |
| **🚀 Potential** | `4-2-3` | **21.2%** | High recent activity with moderate basket size; accelerating. | Mobile banking onboarding perks, recurring deposit automation bonuses. |
| **🌱 Single Product** | `3-1-2` | **10.6%** | Operating only a single savings or current account. | Pre-approved credit lines, discount rates on secondary business current accounts. |
| **⚠️ At-Risk** | `2-3-4` | **12.4%** | Previously active high spenders with declining 90-day cadence. | Proactive outreach from account officers, zero transaction fee promo. |
| **💤 Dormant** | `1-1-1` | **10.6%** | Zero transactions in the last 12 months. | Automated WhatsApp/SMS win-back offers with simple 1-click KYC refresh. |

---

## Regional Analysis & Geospatial Highlights

- **Lagos & Abuja Dominance:** Lagos represents **₦629.5M (33.8%)** of all volume with 1,986 transactions, followed by Abuja with **₦389.9M (20.9%)**.
- **Emerging Hubs:** Port Harcourt (**₦273.2M**) and Kano (**₦162.5M**) demonstrate the highest average ticket size per debit transaction, signaling strong corporate and commercial retail activity.
- **Dormancy Spread:** Peripheral cities (Jos, Calabar, Abeokuta) exhibited a higher dormancy rate (~22%), indicating a need for localized digital banking adoption programs and agent banking kiosks.

---

## Financial Recommendations for Bank Leadership

1. **Protect Salary Anchor Accounts:** Customers receiving salary deposits have an **88% lower dormancy rate**. Establish employer payroll partnerships with mid-tier businesses in Lagos and Abuja.
2. **Reactivate ₦24.3M in Dormant Balances:** 158 dormant accounts hold idle capital. Re-engaging these customers through zero-fee promotions can convert liabilities into active transactional liquidity.
3. **Execute Single-Product Cross-Sell Campaigns:** 53 customers maintain only a single savings account with healthy average balances (>₦1.2M). Introducing them to investment certificates will elevate Net Interest Margin (NIM).
4. **Deploy Automated Outflow Anomaly Alerts:** Implement real-time SQL detection queries (Query 16) to flag debit spikes exceeding 3x customer 90-day averages, drastically reducing unauthorized transaction exposure.

---
*Report engineered by M Akshay Sharma · CSE (Data Analytics) · VIT-AP University*
