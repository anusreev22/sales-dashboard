import sqlite3
import pandas as pd

# ----------------------------
# Load Excel file
# ----------------------------
FILE = "SuperMarket_Analysis.xlsx"  # make sure this file is in the same folder
df = pd.read_excel(FILE, engine="openpyxl")

print("✅ Excel file loaded successfully")
print("📑 Columns found:", df.columns.tolist())

# ----------------------------
# Map columns (auto-detect)
# ----------------------------
date_col = None
for cand in ["Date", "Invoice Date", "date"]:
    if cand in df.columns:
        date_col = cand
        break

product_col = "Product line" if "Product line" in df.columns else None

revenue_col = None
for cand in ["Total", "Sales", "Revenue"]:
    if cand in df.columns:
        revenue_col = cand
        break

if not (date_col and product_col and revenue_col):
    raise ValueError("❌ Could not find required columns (Date, Product line, Sales/Total) in Excel file!")

print(f"📌 Using columns → Date: {date_col}, Product: {product_col}, Revenue: {revenue_col}")

# ----------------------------
# Connect to SQLite database
# ----------------------------
conn = sqlite3.connect("sales.db")
cursor = conn.cursor()

# Create sales table
cursor.execute('''
CREATE TABLE IF NOT EXISTS sales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    product TEXT,
    revenue REAL
)
''')

# ----------------------------
# Insert rows
# ----------------------------
cursor.execute("DELETE FROM sales")  # clear old data if re-running

for _, row in df.iterrows():
    cursor.execute(
        '''
        INSERT INTO sales (date, product, revenue)
        VALUES (?, ?, ?)
        ''',
        (str(row[date_col]), row[product_col], float(row[revenue_col]))
    )

# ----------------------------
# Commit + Close
# ----------------------------
conn.commit()
conn.close()

print("🎉 Database created and populated successfully → sales.db")