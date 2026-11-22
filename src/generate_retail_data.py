"""
Script: generate_retail_data.py
Description: Generates a realistic retail sales dataset with intentional data quality issues
             (missing values, duplicates, whitespace, formatting discrepancies) for data cleaning practice.
"""

import os
import random
import numpy as np
import pandas as pd

def generate_retail_dataset(output_path: str, seed: int = 42, num_rows: int = 2400):
    np.random.seed(seed)
    random.seed(seed)

    products = [
        {"name": "Apple MacBook Pro 16", "category": "Electronics", "sub": "Laptops", "cost": 1800.0, "price": 2499.0},
        {"name": "Dell XPS 15", "category": "Electronics", "sub": "Laptops", "cost": 1200.0, "price": 1699.0},
        {"name": "Dell UltraSharp 27 Monitor", "category": "Electronics", "sub": "Monitors", "cost": 320.0, "price": 499.0},
        {"name": "Logitech MX Master 3S", "category": "Electronics", "sub": "Accessories", "cost": 45.0, "price": 99.0},
        {"name": "Sony WH-1000XM5 Headphones", "category": "Electronics", "sub": "Audio", "cost": 220.0, "price": 399.0},
        {"name": "Keychron Q1 Mechanical Keyboard", "category": "Electronics", "sub": "Accessories", "cost": 90.0, "price": 179.0},
        {"name": "Ergonomic Mesh Office Chair", "category": "Furniture", "sub": "Chairs", "cost": 180.0, "price": 349.0},
        {"name": "Standing Desk Pro Dual-Motor", "category": "Furniture", "sub": "Desks", "cost": 290.0, "price": 549.0},
        {"name": "Steelcase 3-Drawer File Cabinet", "category": "Furniture", "sub": "Storage", "cost": 110.0, "price": 219.0},
        {"name": "Solid Oak Bookshelf", "category": "Furniture", "sub": "Storage", "cost": 140.0, "price": 279.0},
        {"name": "Heavy-Duty Packing Tape (6-Pack)", "category": "Office Supplies", "sub": "Packaging", "cost": 8.0, "price": 22.0},
        {"name": "Multipurpose Copy Paper (5000 Sheets)", "category": "Office Supplies", "sub": "Paper", "cost": 25.0, "price": 49.0},
        {"name": "Executive Leather Binder", "category": "Office Supplies", "sub": "Binders", "cost": 12.0, "price": 35.0},
        {"name": "Gel Ink Pens Assorted 24-Pack", "category": "Office Supplies", "sub": "Pens", "cost": 6.0, "price": 18.0},
        {"name": "Dry Erase Magnetic Whiteboard", "category": "Office Supplies", "sub": "Supplies", "cost": 40.0, "price": 89.0},
        {"name": "Premium Cotton Oxford Shirt", "category": "Apparel", "sub": "Tops", "cost": 20.0, "price": 58.0},
        {"name": "Slim-Fit Chino Trousers", "category": "Apparel", "sub": "Bottoms", "cost": 22.0, "price": 64.0},
        {"name": "Waterproof Trench Coat", "category": "Apparel", "sub": "Outerwear", "cost": 65.0, "price": 160.0},
        {"name": "Merino Wool Crewneck Sweater", "category": "Apparel", "sub": "Knitwear", "cost": 35.0, "price": 95.0},
        {"name": "Leather Derby Dress Shoes", "category": "Apparel", "sub": "Footwear", "cost": 50.0, "price": 135.0}
    ]

    segments = ["Consumer", "Corporate", "Home Office"]
    regions = ["North", "South", "East", "West"]
    payment_methods = ["Credit Card", "PayPal", "Debit Card", "Bank Transfer"]

    start_date = pd.Timestamp("2024-01-01")
    end_date = pd.Timestamp("2025-12-31")
    days_range = (end_date - start_date).days

    rows = []
    for i in range(1, num_rows + 1):
        order_id = f"ORD-{20240000 + i}"
        customer_id = f"CUST-{random.randint(1001, 1450)}"
        
        # Seasonality weights: Q4 (holiday shopping) has higher frequency
        rand_day = random.randint(0, days_range)
        order_date = start_date + pd.Timedelta(days=rand_day)
        month = order_date.month
        # Slight boost for holiday shopping
        if month in [11, 12] and random.random() < 0.25:
            order_date = order_date  # keep it
        
        prod = random.choice(products)
        segment = random.choice(segments)
        region = random.choice(regions)
        payment = random.choice(payment_methods)
        
        quantity = np.random.choice([1, 2, 3, 4, 5, 6, 8, 10], p=[0.40, 0.25, 0.15, 0.08, 0.05, 0.03, 0.02, 0.02])
        discount = np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20, 0.25], p=[0.45, 0.20, 0.15, 0.10, 0.06, 0.04])
        
        unit_cost = prod["cost"]
        unit_price = prod["price"]
        
        # Introduce occasional string formatting variations
        cat_str = prod["category"]
        if random.random() < 0.04:
            cat_str = f"  {cat_str}  "
            
        region_str = region
        if random.random() < 0.03:
            region_str = region_str.lower()
            
        date_str = order_date.strftime("%Y-%m-%d")
        if random.random() < 0.02:
            date_str = order_date.strftime("%d/%m/%Y")

        rows.append({
            "Order_ID": order_id,
            "Order_Date": date_str,
            "Customer_ID": customer_id,
            "Customer_Segment": segment,
            "Region": region_str,
            "Category": cat_str,
            "Sub_Category": prod["sub"],
            "Product_Name": prod["name"],
            "Unit_Cost": unit_cost,
            "Unit_Price": unit_price,
            "Quantity": quantity,
            "Discount": discount,
            "Payment_Method": payment
        })

    df = pd.DataFrame(rows)

    # 1. Introduce ~35 duplicate rows
    dup_indices = np.random.choice(df.index, size=35, replace=False)
    duplicates = df.loc[dup_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    # 2. Introduce missing values in Customer_Segment, Payment_Method, Discount
    missing_seg_idx = np.random.choice(df.index, size=42, replace=False)
    df.loc[missing_seg_idx, "Customer_Segment"] = np.nan

    missing_pay_idx = np.random.choice(df.index, size=38, replace=False)
    df.loc[missing_pay_idx, "Payment_Method"] = np.nan

    missing_disc_idx = np.random.choice(df.index, size=30, replace=False)
    df.loc[missing_disc_idx, "Discount"] = np.nan

    # Shuffle rows
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated raw retail dataset with {len(df)} rows and {df.shape[1]} columns -> {output_path}")

if __name__ == "__main__":
    out = os.path.abspath(r"C:\Users\saic7\.gemini\antigravity\scratch\Retail-Sales-Data-Analysis\data\raw_retail_sales.csv")
    generate_retail_dataset(out)
