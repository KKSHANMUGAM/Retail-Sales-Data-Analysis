"""
Module: exploratory_analysis.py
Project: Retail Sales Data Analysis
Author: Portfolio Project
Description: Computes comprehensive sales and profitability analytics, generates 
             publication-ready visualizations, and outputs precise business KPIs.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set clean, professional visual styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.labelsize"] = 11

def run_analysis(data_path: str, viz_dir: str):
    print("=" * 65)
    print("RETAIL SALES EXPLORATORY DATA ANALYSIS & KPI REPORT")
    print("=" * 65)
    df = pd.read_csv(data_path)
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    os.makedirs(viz_dir, exist_ok=True)

    # -------------------------------------------------------------
    # 1. EXECUTIVE KPI SUMMARY
    # -------------------------------------------------------------
    total_orders = len(df)
    unique_customers = df["Customer_ID"].nunique()
    total_units_sold = df["Quantity"].sum()
    total_revenue = df["Total_Revenue"].sum()
    total_cost = df["Total_Cost"].sum()
    total_profit = df["Profit"].sum()
    avg_order_value = df["Total_Revenue"].mean()
    overall_profit_margin = (total_profit / total_revenue) * 100

    print("\n--- EXECUTIVE SUMMARY KPIs ---")
    print(f"Total Transactions:        {total_orders:,}")
    print(f"Unique Customers:          {unique_customers:,}")
    print(f"Total Units Sold:          {total_units_sold:,}")
    print(f"Total Revenue:             ${total_revenue:,.2f}")
    print(f"Total Cost:                ${total_cost:,.2f}")
    print(f"Total Net Profit:          ${total_profit:,.2f}")
    print(f"Average Order Value (AOV): ${avg_order_value:,.2f}")
    print(f"Overall Profit Margin:     {overall_profit_margin:.2f}%")

    # -------------------------------------------------------------
    # 2. MONTHLY SALES & PROFIT TRENDS
    # -------------------------------------------------------------
    monthly = df.groupby("Year_Month").agg(
        Revenue=("Total_Revenue", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "count")
    ).reset_index()

    print("\n--- MONTHLY REVENUE & PROFIT SNAPSHOT (FIRST & LAST 3 MONTHS) ---")
    print(pd.concat([monthly.head(3), monthly.tail(3)]).to_string(index=False))

    # Plot 1: Monthly Sales & Profit Trend
    fig, ax1 = plt.subplots(figsize=(13, 6))
    
    x = np.arange(len(monthly))
    ax1.plot(x, monthly["Revenue"], color="#1f77b4", marker="o", linewidth=2.5, label="Net Revenue ($)")
    ax1.plot(x, monthly["Profit"], color="#2ca02c", marker="s", linewidth=2.5, linestyle="--", label="Net Profit ($)")
    
    ax1.set_title("Monthly Net Revenue and Profit Trend (2024 - 2025)", fontsize=14, weight="bold", pad=15)
    ax1.set_xlabel("Year-Month", labelpad=10, weight="bold")
    ax1.set_ylabel("Amount in USD ($)", labelpad=10, weight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(monthly["Year_Month"], rotation=45, ha="right")
    ax1.yaxis.set_major_formatter("${x:,.0f}")
    ax1.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#cccccc")
    ax1.grid(True, linestyle=":", alpha=0.6)
    
    # Highlight peak month
    peak_idx = monthly["Revenue"].idxmax()
    peak_rev = monthly.loc[peak_idx, "Revenue"]
    peak_ym = monthly.loc[peak_idx, "Year_Month"]
    ax1.annotate(f"Peak: ${peak_rev:,.0f}\n({peak_ym})",
                 xy=(peak_idx, peak_rev),
                 xytext=(peak_idx - 2, peak_rev * 1.05),
                 arrowprops=dict(facecolor="#d62728", shrink=0.08, width=1.5, headwidth=6),
                 fontweight="bold", color="#d62728",
                 bbox=dict(boxstyle="round,pad=0.3", fc="#ffeedd", ec="#d62728", lw=1))

    plt.tight_layout()
    chart1_path = os.path.join(viz_dir, "01_monthly_sales_trend.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"Saved: {chart1_path}")

    # -------------------------------------------------------------
    # 3. CATEGORY & SUB-CATEGORY PERFORMANCE
    # -------------------------------------------------------------
    cat_summary = df.groupby("Category").agg(
        Revenue=("Total_Revenue", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "count"),
        Avg_Margin=("Profit_Margin_Pct", "mean")
    ).reset_index()
    cat_summary["Margin_Pct"] = (cat_summary["Profit"] / cat_summary["Revenue"]) * 100
    cat_summary = cat_summary.sort_values(by="Revenue", ascending=False)

    print("\n--- SALES BY CATEGORY ---")
    print(cat_summary.to_string(index=False))

    # Plot 2: Category Sales vs Profit
    fig, ax = plt.subplots(figsize=(10, 6))
    width = 0.35
    y_pos = np.arange(len(cat_summary))

    bars1 = ax.barh(y_pos - width/2, cat_summary["Revenue"], width, label="Total Revenue", color="#3b82f6")
    bars2 = ax.barh(y_pos + width/2, cat_summary["Profit"], width, label="Total Profit", color="#10b981")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(cat_summary["Category"], fontsize=11, weight="bold")
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter("${x:,.0f}")
    ax.set_xlabel("Amount in USD ($)", weight="bold", labelpad=10)
    ax.set_title("Total Revenue vs. Net Profit by Product Category", fontsize=14, weight="bold", pad=15)
    ax.legend(frameon=True, loc="lower right")

    # Add data labels
    for bar in bars1:
        w = bar.get_width()
        ax.text(w + 5000, bar.get_y() + bar.get_height()/2, f"${w:,.0f}", va="center", ha="left", fontsize=9, color="#1e3a8a", weight="bold")
    for bar in bars2:
        w = bar.get_width()
        ax.text(w + 5000, bar.get_y() + bar.get_height()/2, f"${w:,.0f}", va="center", ha="left", fontsize=9, color="#065f46", weight="bold")

    ax.set_xlim(0, cat_summary["Revenue"].max() * 1.18)
    plt.tight_layout()
    chart2_path = os.path.join(viz_dir, "02_sales_and_profit_by_category.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"Saved: {chart2_path}")

    # -------------------------------------------------------------
    # 4. TOP-SELLING PRODUCTS (REVENUE & PROFIT)
    # -------------------------------------------------------------
    top_prods = df.groupby(["Product_Name", "Category"]).agg(
        Revenue=("Total_Revenue", "sum"),
        Profit=("Profit", "sum"),
        Units=("Quantity", "sum")
    ).reset_index().sort_values(by="Revenue", ascending=False).head(10)

    print("\n--- TOP 10 SELLING PRODUCTS BY REVENUE ---")
    print(top_prods.to_string(index=False))

    # Plot 3: Top 10 Products by Revenue
    fig, ax = plt.subplots(figsize=(11, 7))
    palette = {"Electronics": "#3b82f6", "Furniture": "#f59e0b", "Office Supplies": "#10b981", "Apparel": "#ec4899"}
    colors = [palette.get(c, "#6b7280") for c in top_prods["Category"]]

    bars = ax.barh(top_prods["Product_Name"], top_prods["Revenue"], color=colors, edgecolor="#374151", height=0.65)
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter("${x:,.0f}")
    ax.set_xlabel("Total Net Revenue in USD ($)", weight="bold", labelpad=10)
    ax.set_title("Top 10 Products by Total Net Revenue", fontsize=14, weight="bold", pad=15)

    # Annotate units sold and profit
    for idx, (bar, (_, row)) in enumerate(zip(bars, top_prods.iterrows())):
        w = bar.get_width()
        ax.text(w + 3000, bar.get_y() + bar.get_height()/2,
                f"${w:,.0f} (Profit: ${row['Profit']:,.0f} | Units: {row['Units']})",
                va="center", ha="left", fontsize=8.5, weight="bold", color="#1f2937")

    # Legend for category color coding
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=color, label=cat) for cat, color in palette.items() if cat in top_prods["Category"].values]
    ax.legend(handles=legend_elements, title="Category", loc="lower right", frameon=True)

    ax.set_xlim(0, top_prods["Revenue"].max() * 1.32)
    plt.tight_layout()
    chart3_path = os.path.join(viz_dir, "03_top_selling_products.png")
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f"Saved: {chart3_path}")

    # -------------------------------------------------------------
    # 5. REGIONAL PERFORMANCE & SEGMENT BREAKDOWN
    # -------------------------------------------------------------
    region_summary = df.groupby("Region").agg(
        Revenue=("Total_Revenue", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "count")
    ).reset_index()
    region_summary["Margin_Pct"] = (region_summary["Profit"] / region_summary["Revenue"]) * 100
    region_summary = region_summary.sort_values(by="Revenue", ascending=False)

    print("\n--- REGIONAL PERFORMANCE ---")
    print(region_summary.to_string(index=False))

    # Plot 4: Regional Analysis (Revenue Share + Profit Margin)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))

    # Pie / Donut Chart for Regional Revenue Share
    colors_donut = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd"]
    wedges, texts, autotexts = ax1.pie(
        region_summary["Revenue"],
        labels=region_summary["Region"],
        autopct="%1.1f%%",
        startangle=140,
        colors=colors_donut,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        textprops=dict(weight="bold", fontsize=10)
    )
    for at in autotexts:
        at.set_color("white")
    ax1.set_title("Revenue Contribution by Region", fontsize=13, weight="bold")

    # Bar chart for Regional Profit Margin %
    bar_colors = ["#059669" if m >= 25 else "#d97706" for m in region_summary["Margin_Pct"]]
    bars_reg = ax2.bar(region_summary["Region"], region_summary["Margin_Pct"], color=bar_colors, edgecolor="#374151", width=0.5)
    ax2.set_ylabel("Profit Margin (%)", weight="bold", labelpad=10)
    ax2.set_title("Regional Profit Margin Percentage", fontsize=13, weight="bold")
    ax2.set_ylim(0, max(region_summary["Margin_Pct"]) * 1.25)
    for b in bars_reg:
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width()/2, h + 0.8, f"{h:.1f}%", ha="center", va="bottom", weight="bold", fontsize=10)

    plt.suptitle("Regional Performance Diagnostics", fontsize=15, weight="bold", y=1.02)
    plt.tight_layout()
    chart4_path = os.path.join(viz_dir, "04_regional_performance.png")
    plt.savefig(chart4_path, dpi=300)
    plt.close()
    print(f"Saved: {chart4_path}")

    # -------------------------------------------------------------
    # 6. DISCOUNT IMPACT ON PROFITABILITY
    # -------------------------------------------------------------
    disc_summary = df.groupby("Discount").agg(
        Orders=("Order_ID", "count"),
        Revenue=("Total_Revenue", "sum"),
        Profit=("Profit", "sum"),
        Avg_Profit_Margin=("Profit_Margin_Pct", "mean")
    ).reset_index()

    print("\n--- DISCOUNT RATE IMPACT ON PROFIT MARGIN ---")
    print(disc_summary.to_string(index=False))

    # Plot 5: Discount vs Profit Margin
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x="Discount", y="Profit_Margin_Pct", data=df, ax=ax, palette="Blues_r", showmeans=True,
                meanprops={"marker":"o", "markerfacecolor":"red", "markeredgecolor":"red"})
    ax.set_title("Impact of Promotional Discount Rate on Profit Margin (%)", fontsize=14, weight="bold", pad=15)
    ax.set_xlabel("Applied Discount Rate", weight="bold", labelpad=10)
    ax.set_ylabel("Profit Margin Percentage (%)", weight="bold", labelpad=10)
    ax.axhline(0, color="red", linestyle="--", alpha=0.7, label="Break-Even Threshold (0%)")
    ax.legend(loc="upper right")

    plt.tight_layout()
    chart5_path = os.path.join(viz_dir, "05_discount_vs_profit_margin.png")
    plt.savefig(chart5_path, dpi=300)
    plt.close()
    print(f"Saved: {chart5_path}")
    print("=" * 65)

if __name__ == "__main__":
    d_path = os.path.abspath(r"C:\Users\saic7\.gemini\antigravity\scratch\Retail-Sales-Data-Analysis\data\cleaned_retail_sales.csv")
    v_dir = os.path.abspath(r"C:\Users\saic7\.gemini\antigravity\scratch\Retail-Sales-Data-Analysis\visualizations")
    run_analysis(d_path, v_dir)
