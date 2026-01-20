import requests
import os
from utils.data_processor import *
def fetch_all_products():
    """
    Fetches all products from DummyJSON API

    Returns: list of product dictionaries

    Requirements:
    - Fetch all available products (use limit=100)
    - Handle connection errors with try-except
    - Return empty list if API fails
    - Print status message (success/failure)
    """
    url = "https://dummyjson.com/products?limit=100"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"Failed to fetch products. Status code: {response.status_code}")
            return []

        data = response.json()
        products = data.get("products", [])

        # Keep only required fields
        cleaned_products = []
        for p in products:
            cleaned_products.append({
                "id": p.get("id"),
                "title": p.get("title"),
                "category": p.get("category"),
                "brand": p.get("brand"),
                "price": p.get("price"),
                "rating": p.get("rating")
            })

        print(f"Successfully fetched {len(cleaned_products)} products.")
        return cleaned_products

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []
def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info

    Parameters: api_products from fetch_all_products()

    Returns: dictionary mapping product IDs to info

    Expected Output Format:
    {
        1: {'title': 'iPhone 9', 'category': 'smartphones', 'brand': 'Apple', 'rating': 4.69},
        2: {'title': 'iPhone X', 'category': 'smartphones', 'brand': 'Apple', 'rating': 4.44},
        ...
    }
    """
    product_map = {}

    for p in api_products:
        try:
            product_id = p.get("id")
            if product_id is None:
                continue

            product_map[product_id] = {
                "title": p.get("title"),
                "category": p.get("category"),
                "brand": p.get("brand"),
                "rating": p.get("rating")
            }
        except AttributeError:
            # In case an item is not a dictionary
            continue

    return product_map



def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information

    Parameters:
    - transactions: list of transaction dictionaries
    - product_mapping: dictionary from create_product_mapping()

    Returns: list of enriched transaction dictionaries

    File Output:
    - Save enriched data to 'data/enriched_sales_data.txt'
    - Use same pipe-delimited format
    - Include new columns in header
    """
    enriched_transactions = []

    for tx in transactions:
        try:
            enriched_tx = tx.copy()

            # Extract numeric ID from ProductID (P101 -> 101)
            product_id_str = str(tx.get("ProductID", "")).strip()

            numeric_id = None
            if product_id_str.startswith("P"):
                numeric_part = product_id_str[1:]
                if numeric_part.isdigit():
                    numeric_id = int(numeric_part)

            # Default enrichment fields
            enriched_tx["API_Category"] = None
            enriched_tx["API_Brand"] = None
            enriched_tx["API_Rating"] = None
            enriched_tx["API_Match"] = False

            # Enrich if mapping exists
            if numeric_id is not None and numeric_id in product_mapping:
                api_info = product_mapping[numeric_id]
                enriched_tx["API_Category"] = api_info.get("category")
                enriched_tx["API_Brand"] = api_info.get("brand")
                enriched_tx["API_Rating"] = api_info.get("rating")
                enriched_tx["API_Match"] = True

            enriched_transactions.append(enriched_tx)

        except Exception:
            # Gracefully handle unexpected errors
            tx_copy = tx.copy()
            tx_copy["API_Category"] = None
            tx_copy["API_Brand"] = None
            tx_copy["API_Rating"] = None
            tx_copy["API_Match"] = False
            enriched_transactions.append(tx_copy)

    # Save to file
    save_enriched_data(enriched_transactions, filename="data/enriched_sales_data.txt")

    return enriched_transactions


def save_enriched_data(enriched_transactions, filename="data/enriched_sales_data.txt"):
    """
    Saves enriched transactions back to file

    Expected File Format:
    TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region|API_Category|API_Brand|API_Rating|API_Match
    T001|2024-12-01|P101|Laptop|2|45000.0|C001|North|laptops|Apple|4.7|True
    ...
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    headers = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region",
        "API_Category", "API_Brand", "API_Rating", "API_Match"
    ]

    with open(filename, "w", encoding="utf-8") as f:
        # Write header
        f.write("|".join(headers) + "\n")

        # Write rows
        for tx in enriched_transactions:
            row = []
            for h in headers:
                value = tx.get(h)

                # Handle None values
                if value is None:
                    row.append("")
                else:
                    row.append(str(value))

            f.write("|".join(row) + "\n")

import os
from datetime import datetime

def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """
    Generates a comprehensive formatted text report with 8 required sections.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # ---------------- HELPERS ----------------
    def fmt_money(x):
        try:
            return f"₹{x:,.2f}"
        except Exception:
            return "₹0.00"

    def fmt_pct(x):
        try:
            return f"{x:.2f}%"
        except Exception:
            return "0.00%"

    def safe_str(x):
        return "" if x is None else str(x)

    def line(char="=", width=60):
        return char * width

    # ---------------- METRICS ----------------
    total_records = len(transactions)

    total_revenue = calculate_total_revenue(transactions)
    total_transactions = len(transactions)
    avg_order_value = (total_revenue / total_transactions) if total_transactions > 0 else 0.0

    # Date range
    dates = sorted([t.get("Date") for t in transactions if t.get("Date")])
    date_range = (dates[0], dates[-1]) if dates else ("N/A", "N/A")

    # Region stats
    region_stats = region_wise_sales(transactions)

    # Top products
    top_products = top_selling_products(transactions, n=5)

    # Customer stats
    customer_stats = customer_analysis(transactions)
    top_customers = []
    rank = 1
    for cust_id, stats in customer_stats.items():
        top_customers.append((cust_id, stats["total_spent"], stats["purchase_count"]))
        rank += 1
        if len(top_customers) == 5:
            break

    # Daily trend
    daily_trend = daily_sales_trend(transactions)

    # Peak sales day
    peak_date, peak_rev, peak_count = find_peak_sales_day(transactions)

    # Low performing products
    low_products = low_performing_products(transactions, threshold=10)

    # Avg transaction value per region
    avg_tx_value_region = {}
    for r, stats in region_stats.items():
        cnt = stats.get("transaction_count", 0)
        avg_tx_value_region[r] = (stats.get("total_sales", 0.0) / cnt) if cnt > 0 else 0.0

    # API enrichment summary
    enriched_count = 0
    not_enriched_products = set()

    for tx in enriched_transactions:
        if tx.get("API_Match") is True:
            enriched_count += 1
        else:
            not_enriched_products.add(tx.get("ProductID"))

    total_enriched_records = len(enriched_transactions)
    success_rate = (enriched_count / total_enriched_records * 100) if total_enriched_records > 0 else 0.0

    # ---------------- REPORT BUILD ----------------
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines = []

    # 1) HEADER
    report_lines.append(line("="))
    report_lines.append("           SALES ANALYTICS REPORT")
    report_lines.append(f"         Generated: {now}")
    report_lines.append(f"         Records Processed: {total_records}")
    report_lines.append(line("="))
    report_lines.append("")

    # 2) OVERALL SUMMARY
    report_lines.append("OVERALL SUMMARY")
    report_lines.append(line("-", 60))
    report_lines.append(f"{'Total Revenue:':20} {fmt_money(total_revenue)}")
    report_lines.append(f"{'Total Transactions:':20} {total_transactions}")
    report_lines.append(f"{'Average Order Value:':20} {fmt_money(avg_order_value)}")
    report_lines.append(f"{'Date Range:':20} {date_range[0]} to {date_range[1]}")
    report_lines.append("")

    # 3) REGION-WISE PERFORMANCE
    report_lines.append("REGION-WISE PERFORMANCE")
    report_lines.append(line("-", 60))
    report_lines.append(f"{'Region':10}{'Sales':15}{'% of Total':12}{'Transactions':12}")
    for r, stats in region_stats.items():
        report_lines.append(
            f"{r:10}{fmt_money(stats['total_sales']):15}{fmt_pct(stats['percentage']):12}{stats['transaction_count']:12}"
        )
    report_lines.append("")

    # 4) TOP 5 PRODUCTS
    report_lines.append("TOP 5 PRODUCTS")
    report_lines.append(line("-", 60))
    report_lines.append(f"{'Rank':6}{'Product Name':25}{'Qty Sold':10}{'Revenue':15}")
    for i, (name, qty, rev) in enumerate(top_products, start=1):
        report_lines.append(f"{i:<6}{name[:24]:25}{qty:<10}{fmt_money(rev):15}")
    report_lines.append("")

    # 5) TOP 5 CUSTOMERS
    report_lines.append("TOP 5 CUSTOMERS")
    report_lines.append(line("-", 60))
    report_lines.append(f"{'Rank':6}{'Customer ID':15}{'Total Spent':15}{'Orders':10}")
    for i, (cust_id, spent, orders) in enumerate(top_customers, start=1):
        report_lines.append(f"{i:<6}{cust_id:<15}{fmt_money(spent):15}{orders:<10}")
    report_lines.append("")

    # 6) DAILY SALES TREND
    report_lines.append("DAILY SALES TREND")
    report_lines.append(line("-", 60))
    report_lines.append(f"{'Date':12}{'Revenue':15}{'Transactions':15}{'Unique Customers':15}")
    for d, stats in daily_trend.items():
        report_lines.append(
            f"{d:<12}{fmt_money(stats['revenue']):15}{stats['transaction_count']:<15}{stats['unique_customers']:<15}"
        )
    report_lines.append("")

    # 7) PRODUCT PERFORMANCE ANALYSIS
    report_lines.append("PRODUCT PERFORMANCE ANALYSIS")
    report_lines.append(line("-", 60))
    report_lines.append(f"Best Selling Day: {peak_date} | Revenue: {fmt_money(peak_rev)} | Transactions: {peak_count}")
    report_lines.append("")

    if low_products:
        report_lines.append("Low Performing Products (Total Quantity < 10)")
        report_lines.append(f"{'Product Name':25}{'Qty Sold':10}{'Revenue':15}")
        for name, qty, rev in low_products:
            report_lines.append(f"{name[:24]:25}{qty:<10}{fmt_money(rev):15}")
    else:
        report_lines.append("Low Performing Products: None")
    report_lines.append("")

    report_lines.append("Average Transaction Value per Region")
    report_lines.append(f"{'Region':10}{'Avg Transaction Value':20}")
    for r, avg_val in sorted(avg_tx_value_region.items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"{r:10}{fmt_money(avg_val):20}")
    report_lines.append("")

    # 8) API ENRICHMENT SUMMARY
    report_lines.append("API ENRICHMENT SUMMARY")
    report_lines.append(line("-", 60))
    report_lines.append(f"{'Total records enriched:':25} {enriched_count}")
    report_lines.append(f"{'Success rate:':25} {success_rate:.2f}%")
    report_lines.append("Products not enriched (ProductIDs):")

    if not_enriched_products:
        for pid in sorted([p for p in not_enriched_products if p]):
            report_lines.append(f" - {pid}")
    else:
        report_lines.append(" - None")
    report_lines.append("")

    # ---------------- WRITE TO FILE ----------------
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"Sales report generated successfully: {output_file}")
