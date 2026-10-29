#!/usr/bin/env python3
"""
RFM Analytics & Machine Learning Customer Clustering Engine
Calculates Recency, Frequency, Monetary (RFM) metrics and trains unsupervised K-Means model.
Generates publication-quality charts in assets/ and exports segment tables.
Author: M Akshay Sharma (@akshaysharma2005)
"""

import os
import sqlite3
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Set style
plt.style.use('dark_background')
plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, sans-serif'
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 0.8

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DB_PATH = os.path.join(DATA_DIR, "bank_analytics.db")

def run_rfm_and_clustering():
    print("[*] Loading data from SQLite database...")
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        c.customer_id,
        c.name,
        c.city,
        c.gender,
        c.signup_date,
        COUNT(t.transaction_id) as total_txns,
        COUNT(DISTINCT a.account_id) as total_accounts,
        MAX(t.transaction_date) as last_txn_date,
        SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END) as total_spent,
        SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END) as total_inflow,
        SUM(t.amount) as total_volume,
        ROUND(AVG(t.amount), 2) as avg_txn_value,
        SUM(a.balance) as total_balance
    FROM customers c
    JOIN accounts a ON c.customer_id = a.customer_id
    LEFT JOIN transactions t ON a.account_id = t.account_id
    GROUP BY c.customer_id, c.name, c.city, c.gender, c.signup_date
    """
    df = pd.read_sql_query(query, conn)
    
    # Snapshot analysis date: 2026-10-29
    snapshot_date = datetime.date(2026, 10, 29)
    
    # Calculate Recency (days since last transaction)
    df['last_txn_date'] = pd.to_datetime(df['last_txn_date']).dt.date
    df['recency'] = df['last_txn_date'].apply(
        lambda d: (snapshot_date - d).days if pd.notnull(d) else 999
    )
    
    # Frequency: total transactions
    df['frequency'] = df['total_txns'].fillna(0).astype(int)
    
    # Monetary: total volume processed
    df['monetary'] = df['total_volume'].fillna(0)
    
    # 1. RFM Scoring using quintiles (1-5)
    # Recency: lower is better -> reverse bins
    df['r_score'] = pd.qcut(df['recency'].rank(method='first'), q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    df['f_score'] = pd.qcut(df['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    df['m_score'] = pd.qcut(df['monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    df['rfm_score'] = df['r_score'].astype(str) + df['f_score'].astype(str) + df['m_score'].astype(str)
    
    # 2. Rule-based RFM Segment Assignment
    def assign_segment(row):
        r, f, m = row['r_score'], row['f_score'], row['m_score']
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f <= 3 and m >= 2:
            return 'Potential Loyalists'
        elif r >= 3 and f <= 2:
            return 'New & Single Product'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        else:
            return 'Dormant Accounts'
            
    df['segment'] = df.apply(assign_segment, axis=1)
    
    # 3. Unsupervised K-Means Clustering on Log-transformed Normalized RFM
    print("[*] Training K-Means clustering algorithm...")
    rfm_features = df[['recency', 'frequency', 'monetary', 'total_balance']].copy()
    
    # Handle zeros and log transform to manage positive skewness
    rfm_log = np.log1p(rfm_features)
    
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_log)
    
    # Optimal clusters: K=4 for behavioral grouping
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(rfm_scaled)
    
    # PCA for 2D visualization
    pca = PCA(n_components=2, random_state=42)
    pca_coords = pca.fit_transform(rfm_scaled)
    df['pca_x'] = pca_coords[:, 0]
    df['pca_y'] = pca_coords[:, 1]
    
    print("[*] Cluster Summary:")
    cluster_summary = df.groupby('cluster')[['recency', 'frequency', 'monetary', 'total_balance']].mean()
    print(cluster_summary)
    
    # Save enriched RFM table
    output_csv = os.path.join(DATA_DIR, "rfm_segments.csv")
    df.to_csv(output_csv, index=False)
    print(f"[✓] Saved RFM segments to {output_csv}")
    
    # Also write into SQLite DB table
    df.to_sql('customer_rfm_segments', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    
    # 4. Generate Publication-Quality Charts in assets/
    generate_charts(df)
    
def generate_charts(df):
    print("[*] Generating high-resolution graphics in assets/...")
    
    # Palette
    palette = ['#00f2fe', '#10b981', '#a855f7', '#f59e0b', '#3b82f6', '#f43f5e']
    
    # --- CHART 1: PCA Cluster Scatter Plot ---
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300, facecolor='#0b0f19')
    ax.set_facecolor('#0d1527')
    
    clusters = sorted(df['cluster'].unique())
    cluster_labels = {
        0: 'Tier 1: High Net-Worth Active',
        1: 'Tier 2: Steady Core Retail',
        2: 'Tier 3: Low-Engagement / Single Product',
        3: 'Tier 4: Dormant & At-Risk Accounts'
    }
    
    for c in clusters:
        sub = df[df['cluster'] == c]
        ax.scatter(
            sub['pca_x'], sub['pca_y'], 
            c=palette[c % len(palette)], 
            label=cluster_labels.get(c, f"Cluster {c}"),
            alpha=0.75, s=65, edgecolors='none'
        )
        
    ax.set_title("Machine Learning Customer Segmentation (PCA 2D Cluster Space)", 
                 fontsize=14, fontweight='bold', color='#ffffff', pad=15)
    ax.set_xlabel("Principal Component 1 (Transaction Frequency & Volume)", fontsize=11, color='#94a3b8', labelpad=10)
    ax.set_ylabel("Principal Component 2 (Recency vs Inactivity)", fontsize=11, color='#94a3b8', labelpad=10)
    ax.tick_params(colors='#64748b', labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.15, color='#ffffff')
    
    legend = ax.legend(frameon=True, facecolor='#111c33', edgecolor='#1e293b', 
                       fontsize=9.5, labelcolor='#e2e8f0', loc='upper right')
    
    plt.tight_layout()
    chart1_path = os.path.join(ASSETS_DIR, "cluster_scatter.png")
    plt.savefig(chart1_path, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"[✓] Generated {chart1_path}")
    
    # --- CHART 2: Segment Distribution Bar & Share ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300, facecolor='#0b0f19')
    ax1.set_facecolor('#0d1527')
    ax2.set_facecolor('#0d1527')
    
    seg_counts = df['segment'].value_counts()
    colors = ['#00f2fe', '#10b981', '#8b5cf6', '#38bdf8', '#f59e0b', '#f43f5e']
    
    # Bar Chart
    bars = ax1.barh(seg_counts.index, seg_counts.values, color=colors[:len(seg_counts)], height=0.6)
    ax1.set_title("Customer Population per RFM Segment", fontsize=13, fontweight='bold', color='#ffffff', pad=12)
    ax1.set_xlabel("Number of Customers", fontsize=10.5, color='#94a3b8')
    ax1.tick_params(colors='#94a3b8', labelsize=10)
    ax1.grid(axis='x', linestyle='--', alpha=0.2, color='#ffffff')
    ax1.invert_yaxis()
    
    for bar in bars:
        w = bar.get_width()
        ax1.text(w + 3, bar.get_y() + bar.get_height()/2, f'{int(w)}', 
                 va='center', color='#ffffff', fontweight='bold', fontsize=9.5)
                 
    # Donut Chart
    wedges, texts, autotexts = ax2.pie(
        seg_counts.values, 
        labels=seg_counts.index, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colors[:len(seg_counts)],
        wedgeprops=dict(width=0.45, edgecolor='#0b0f19', linewidth=2),
        textprops=dict(color='#cbd5e1', fontsize=9.5)
    )
    for at in autotexts:
        at.set_color('#ffffff')
        at.set_fontweight('bold')
        at.set_fontsize(9)
        
    ax2.set_title("Portfolio Segment Share (%)", fontsize=13, fontweight='bold', color='#ffffff', pad=12)
    
    plt.tight_layout()
    chart2_path = os.path.join(ASSETS_DIR, "segment_distribution.png")
    plt.savefig(chart2_path, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"[✓] Generated {chart2_path}")
    
    # --- CHART 3: Monthly Volume & Transaction Count Trend ---
    conn = sqlite3.connect(DB_PATH)
    trend_df = pd.read_sql_query("""
    SELECT 
        substr(transaction_date, 1, 7) as month,
        COUNT(*) as txn_count,
        SUM(amount) / 1000000.0 as volume_millions,
        SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) / 1000000.0 as credit_vol,
        SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) / 1000000.0 as debit_vol
    FROM transactions
    WHERE transaction_date >= '2024-11-01'
    GROUP BY month
    ORDER BY month ASC
    """, conn)
    conn.close()
    
    if len(trend_df) > 0:
        fig, ax1 = plt.subplots(figsize=(12, 5.5), dpi=300, facecolor='#0b0f19')
        ax1.set_facecolor('#0d1527')
        
        ax2 = ax1.twinx()
        
        # Bar for volume
        x = np.arange(len(trend_df))
        ax1.bar(x - 0.15, trend_df['credit_vol'], width=0.3, label='Credit Inflow (₦M)', color='#10b981', alpha=0.85)
        ax1.bar(x + 0.15, trend_df['debit_vol'], width=0.3, label='Debit Outflow (₦M)', color='#00f2fe', alpha=0.85)
        
        # Line for transaction count
        ax2.plot(x, trend_df['txn_count'], color='#f59e0b', marker='o', linewidth=2.5, label='Txn Count')
        
        ax1.set_title("Monthly Transaction Volume (₦ Millions) vs. Frequency Trend", 
                      fontsize=14, fontweight='bold', color='#ffffff', pad=15)
        ax1.set_xticks(x)
        ax1.set_xticklabels(trend_df['month'], rotation=45, ha='right', color='#94a3b8', fontsize=9)
        ax1.set_ylabel("Transaction Volume (₦ Millions)", color='#38bdf8', fontsize=11, labelpad=10)
        ax2.set_ylabel("Monthly Transaction Count", color='#f59e0b', fontsize=11, labelpad=10)
        
        ax1.tick_params(colors='#94a3b8')
        ax2.tick_params(colors='#94a3b8')
        ax1.grid(True, linestyle='--', alpha=0.15, color='#ffffff')
        
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', 
                   facecolor='#111c33', edgecolor='#1e293b', labelcolor='#ffffff', fontsize=9.5)
        
        plt.tight_layout()
        chart3_path = os.path.join(ASSETS_DIR, "monthly_volume_trend.png")
        plt.savefig(chart3_path, facecolor=fig.get_facecolor(), bbox_inches='tight')
        plt.close()
        print(f"[✓] Generated {chart3_path}")
        
    print("[✓] All charts generated successfully!")

if __name__ == "__main__":
    run_rfm_and_clustering()
