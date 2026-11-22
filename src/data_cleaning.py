"""
Module: data_cleaning.py
Project: Retail Sales Data Analysis
Author: Portfolio Project
Description: Handles data quality assessment, deduplication, missing value imputation,
             type casting, string standardization, and derived financial calculations.
"""

import os
import pandas as pd
import numpy as np

def clean_retail_data(input_path: str, output_path: str) -> pd.DataFrame:
    print("=" * 60)
    print("STEP 1: LOADING RAW DATASET")
    print("=" * 60)
    df = pd.read_csv(input_path)
    initial_rows = len(df)
    print(f"Loaded raw records: {initial_rows} rows, {df.shape[1]} columns")

    # 1. Check Missing Values & Duplicates
    print("\n--- Initial Data Quality Diagnostics ---")
    missing_summary = df.isnull().sum()
    print("Missing values per column:\n", missing_summary[missing_summary > 0])
    
    duplicates_count = df.duplicated(subset=["Order_ID"]).sum()
    print(f"Duplicate Order_ID records detected: {duplicates_count}")

    # 2. Deduplication
    df = df.drop_duplicates(subset=["Order_ID"], keep="first").copy()
    print(f"Rows after removing duplicates: {len(df)} (Dropped {initial_rows - len(df)} duplicate records)")

    # 3. String Cleaning & Standardization
    print("\n--- Cleaning String & Categorical Features ---")
    text_cols = ["Customer_Segment", "Region", "Category", "Sub_Category", "Product_Name", "Payment_Method"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Standardize Region casing (e.g. 'north' -> 'North')
    df["Region"] = df["Region"].str.capitalize()
    df["Category"] = df["Category"].str.title()

    # 4. Handle Missing Values
    print("\n--- Imputing Missing Values ---")
    # Replace 'nan' strings that might have resulted from stripping with np.nan
    df.replace({"Customer_Segment": {"nan": np.nan}, "Payment_Method": {"nan": np.nan}}, inplace=True)
    
    # Impute missing Customer_Segment with Mode
    mode_segment = df["Customer_Segment"].mode()[0]
    df["Customer_Segment"] = df["Customer_Segment"].fillna(mode_segment)
    print(f"Imputed Customer_Segment nulls with mode: '{mode_segment}'")

    # Impute missing Payment_Method with Mode
    mode_payment = df["Payment_Method"].mode()[0]
    df["Payment_Method"] = df["Payment_Method"].fillna(mode_payment)
    print(f"Imputed Payment_Method nulls with mode: '{mode_payment}'")

    # Impute missing Discount with 0.0 (no discount applied)
    df["Discount"] = df["Discount"].fillna(0.0)
    print("Imputed Discount nulls with default: 0.0")

    # 5. Date Parsing & Calendar Feature Extraction
    print("\n--- Parsing Dates & Extracting Time Intelligence Features ---")
    # Using format='mixed' handles multiple formats like YYYY-MM-DD and DD/MM/YYYY seamlessly
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="mixed", dayfirst=True)
    df["Year"] = df["Order_Date"].dt.year
    df["Month"] = df["Order_Date"].dt.month
    df["Month_Name"] = df["Order_Date"].dt.strftime("%b")
    df["Year_Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    df["Quarter"] = "Q" + df["Order_Date"].dt.quarter.astype(str)
    df["Day_Name"] = df["Order_Date"].dt.day_name()

    # 6. Financial Metric Calculations
    print("\n--- Engineering Financial KPIs ---")
    # Gross Sales = Quantity * Unit_Price
    df["Gross_Sales"] = (df["Quantity"] * df["Unit_Price"]).round(2)
    # Discount Amount = Gross Sales * Discount
    df["Discount_Amount"] = (df["Gross_Sales"] * df["Discount"]).round(2)
    # Net Revenue = Gross Sales - Discount Amount
    df["Total_Revenue"] = (df["Gross_Sales"] - df["Discount_Amount"]).round(2)
    # Total Cost = Quantity * Unit_Cost
    df["Total_Cost"] = (df["Quantity"] * df["Unit_Cost"]).round(2)
    # Profit = Total Revenue - Total Cost
    df["Profit"] = (df["Total_Revenue"] - df["Total_Cost"]).round(2)
    # Profit Margin % = (Profit / Total Revenue) * 100
    df["Profit_Margin_Pct"] = ((df["Profit"] / df["Total_Revenue"]) * 100).round(2)

    # Sort chronological by Order_Date
    df.sort_values(by="Order_Date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # 7. Verification of Clean Data
    print("\n--- Post-Cleaning Validation ---")
    print(f"Total Clean Records: {len(df)}")
    print(f"Remaining Missing Values: {df.isnull().sum().sum()}")
    print(f"Date Range: {df['Order_Date'].min().date()} to {df['Order_Date'].max().date()}")
    print(f"Total Revenue Generated: ${df['Total_Revenue'].sum():,.2f}")
    print(f"Total Profit Generated: ${df['Profit'].sum():,.2f}")
    print(f"Overall Profit Margin: {(df['Profit'].sum() / df['Total_Revenue'].sum() * 100):.2f}%")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\nSuccessfully exported cleaned dataset to: {output_path}")
    print("=" * 60)
    return df

if __name__ == "__main__":
    in_file = os.path.abspath(r"C:\Users\saic7\.gemini\antigravity\scratch\Retail-Sales-Data-Analysis\data\raw_retail_sales.csv")
    out_file = os.path.abspath(r"C:\Users\saic7\.gemini\antigravity\scratch\Retail-Sales-Data-Analysis\data\cleaned_retail_sales.csv")
    clean_retail_data(in_file, out_file)
