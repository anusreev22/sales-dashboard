from flask import Flask, jsonify, request
import pandas as pd
from sqlalchemy import create_engine
import os

app = Flask(__name__)

# ---------- File Handling ----------
EXCEL_FILE = "SuperMarket_Analysis.xlsx"
CSV_FILE = "SuperMarket Analysis.xlsx"  # your current file (but actually CSV)


def ensure_excel_file():
    """Convert CSV file to real Excel if needed"""
    if not os.path.exists(EXCEL_FILE):
        if os.path.exists(CSV_FILE):
            print("Detected CSV with .xlsx extension. Converting to real Excel...")
            df = pd.read_csv(CSV_FILE)
            df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
            print(f"Converted and saved as {EXCEL_FILE}")
        else:
            raise FileNotFoundError("Neither Excel nor CSV file found!")


# ---------- Data Reading ----------
def read_excel_data():
    ensure_excel_file()
    df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
    return df


def read_sql_data():
    engine = create_engine("sqlite:///sales.db")
    df = pd.read_sql("SELECT * FROM sales", con=engine)
    return df


# ---------- API Endpoints ----------
@app.route("/")
def home():
    return {
        "endpoints": [
            "/api/xlsx",
            "/api/sql",
            "/api/sales?source=xlsx&product=Health%20and%20Beauty",
            "/api/sales?source=sql&city=Yangon&gender=Female&payment=Cash&limit=5&offset=0",
        ],
        "message": "Welcome to the Enhanced Sales API!",
    }


@app.route("/api/xlsx", methods=["GET"])
def get_excel_data():
    df = read_excel_data()
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/sql", methods=["GET"])
def get_sql_data():
    df = read_sql_data()
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/sales", methods=["GET"])
def get_sales_data():
    source = request.args.get("source", "xlsx")

    if source == "xlsx":
        df = read_excel_data()
    else:
        df = read_sql_data()

    # Optional filters
    product = request.args.get("product")
    city = request.args.get("city")
    gender = request.args.get("gender")
    payment = request.args.get("payment")
    limit = request.args.get("limit", type=int)
    offset = request.args.get("offset", type=int, default=0)

    if product:
        df = df[df["Product line"] == product]
    if city:
        df = df[df["City"] == city]
    if gender:
        df = df[df["Gender"] == gender]
    if payment:
        df = df[df["Payment"] == payment]

    if limit is not None:
        df = df.iloc[offset : offset + limit]

    return jsonify(df.to_dict(orient="records"))


# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
