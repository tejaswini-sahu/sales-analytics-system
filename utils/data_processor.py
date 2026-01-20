def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions

    Returns: float (total revenue)

    Expected Output: Single number representing sum of (Quantity * UnitPrice)
    Example: 1545000.50
    """
    total = 0.0

    for tx in transactions:
        try:
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
            total += qty * price
        except (KeyError, TypeError, ValueError):
            # Skip any bad/incomplete transaction records
            continue

    return total

def region_wise_sales(transactions):
    """
    Analyzes sales by region

    Returns: dictionary with region statistics

    Expected Output Format:
    {
        'North': {
            'total_sales': 450000.0,
            'transaction_count': 15,
            'percentage': 29.13
        },
        'South': {...},
        ...
    }

    Requirements:
    - Calculate total sales per region
    - Count transactions per region
    - Calculate percentage of total sales
    - Sort by total_sales in descending order
    """
    region_stats = {}
    grand_total = 0.0

    # 1) Compute totals + counts
    for tx in transactions:
        try:
            region = str(tx["Region"]).strip()
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
        except (KeyError, TypeError, ValueError):
            continue

        if not region:
            continue

        amount = qty * price
        grand_total += amount

        if region not in region_stats:
            region_stats[region] = {"total_sales": 0.0, "transaction_count": 0}

        region_stats[region]["total_sales"] += amount
        region_stats[region]["transaction_count"] += 1

    # 2) Add percentage
    for region in region_stats:
        if grand_total > 0:
            pct = (region_stats[region]["total_sales"] / grand_total) * 100
        else:
            pct = 0.0
        region_stats[region]["percentage"] = round(pct, 2)

    # 3) Sort by total_sales (descending)
    region_stats_sorted = dict(
        sorted(
            region_stats.items(),
            key=lambda x: x[1]["total_sales"],
            reverse=True
        )
    )

    return region_stats_sorted

def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold

    Returns: list of tuples

    Expected Output Format:
    [
        ('Laptop', 45, 2250000.0),  # (ProductName, TotalQuantity, TotalRevenue)
        ('Mouse', 38, 19000.0),
        ...
    ]

    Requirements:
    - Aggregate by ProductName
    - Calculate total quantity sold
    - Calculate total revenue for each product
    - Sort by TotalQuantity descending
    - Return top n products
    """
    product_summary = {}

    for tx in transactions:
        try:
            name = str(tx["ProductName"]).strip()
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
        except (KeyError, TypeError, ValueError):
            continue

        if not name:
            continue

        revenue = qty * price

        if name not in product_summary:
            product_summary[name] = {"total_qty": 0, "total_revenue": 0.0}

        product_summary[name]["total_qty"] += qty
        product_summary[name]["total_revenue"] += revenue

    # Convert to list of tuples
    result = []
    for name, stats in product_summary.items():
        result.append((name, stats["total_qty"], stats["total_revenue"]))

    # Sort by quantity descending (if tie, sort by revenue descending)
    result.sort(key=lambda x: (x[1], x[2]), reverse=True)

    return result[:n]

def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns

    Returns: dictionary of customer statistics

    Expected Output Format:
    {
        'C001': {
            'total_spent': 95000.0,
            'purchase_count': 3,
            'avg_order_value': 31666.67,
            'products_bought': ['Laptop', 'Mouse', 'Keyboard']
        },
        'C002': {...},
        ...
    }

    Requirements:
    - Calculate total amount spent per customer
    - Count number of purchases
    - Calculate average order value
    - List unique products bought
    - Sort by total_spent descending
    """
    customer_stats = {}

    # 1) Aggregate totals, counts, and unique products
    for tx in transactions:
        try:
            customer_id = str(tx["CustomerID"]).strip()
            product_name = str(tx["ProductName"]).strip()
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
        except (KeyError, TypeError, ValueError):
            continue

        if not customer_id:
            continue

        amount = qty * price

        if customer_id not in customer_stats:
            customer_stats[customer_id] = {
                "total_spent": 0.0,
                "purchase_count": 0,
                "products_bought": set()
            }

        customer_stats[customer_id]["total_spent"] += amount
        customer_stats[customer_id]["purchase_count"] += 1

        if product_name:
            customer_stats[customer_id]["products_bought"].add(product_name)

    # 2) Calculate avg order value + convert set -> sorted list
    for cust_id, stats in customer_stats.items():
        count = stats["purchase_count"]
        total = stats["total_spent"]

        stats["avg_order_value"] = round(total / count, 2) if count > 0 else 0.0
        stats["products_bought"] = sorted(list(stats["products_bought"]))

    # 3) Sort by total_spent descending
    customer_stats_sorted = dict(
        sorted(
            customer_stats.items(),
            key=lambda x: x[1]["total_spent"],
            reverse=True
        )
    )

    return customer_stats_sorted

def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date

    Returns: dictionary sorted by date

    Expected Output Format:
    {
        '2024-12-01': {
            'revenue': 125000.0,
            'transaction_count': 8,
            'unique_customers': 6
        },
        '2024-12-02': {...},
        ...
    }

    Requirements:
    - Group by date
    - Calculate daily revenue
    - Count daily transactions
    - Count unique customers per day
    - Sort chronologically
    """
    daily_stats = {}

    # 1) Group and aggregate
    for tx in transactions:
        try:
            date = str(tx["Date"]).strip()
            customer_id = str(tx["CustomerID"]).strip()
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
        except (KeyError, TypeError, ValueError):
            continue

        if not date:
            continue

        revenue = qty * price

        if date not in daily_stats:
            daily_stats[date] = {
                "revenue": 0.0,
                "transaction_count": 0,
                "unique_customers": set()
            }

        daily_stats[date]["revenue"] += revenue
        daily_stats[date]["transaction_count"] += 1

        if customer_id:
            daily_stats[date]["unique_customers"].add(customer_id)

    # 2) Convert unique customer set -> count
    for date in daily_stats:
        daily_stats[date]["unique_customers"] = len(daily_stats[date]["unique_customers"])

    # 3) Sort chronologically (works for YYYY-MM-DD format)
    daily_stats_sorted = dict(sorted(daily_stats.items(), key=lambda x: x[0]))

    return daily_stats_sorted

def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue

    Returns: tuple (date, revenue, transaction_count)

    Expected Output Format:
    ('2024-12-15', 185000.0, 12)
    """
    daily_totals = {}

    for tx in transactions:
        try:
            date = str(tx["Date"]).strip()
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
        except (KeyError, TypeError, ValueError):
            continue

        if not date:
            continue

        revenue = qty * price

        if date not in daily_totals:
            daily_totals[date] = {"revenue": 0.0, "count": 0}

        daily_totals[date]["revenue"] += revenue
        daily_totals[date]["count"] += 1

    if not daily_totals:
        return (None, 0.0, 0)

    peak_date, peak_data = max(daily_totals.items(), key=lambda x: x[1]["revenue"])

    return (peak_date, peak_data["revenue"], peak_data["count"])

def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales

    Returns: list of tuples

    Expected Output Format:
    [
        ('Webcam', 4, 12000.0),  # (ProductName, TotalQuantity, TotalRevenue)
        ('Headphones', 7, 10500.0),
        ...
    ]

    Requirements:
    - Find products with total quantity < threshold
    - Include total quantity and revenue
    - Sort by TotalQuantity ascending
    """
    product_summary = {}

    # Aggregate quantity + revenue per product
    for tx in transactions:
        try:
            name = str(tx["ProductName"]).strip()
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
        except (KeyError, TypeError, ValueError):
            continue

        if not name:
            continue

        revenue = qty * price

        if name not in product_summary:
            product_summary[name] = {"total_qty": 0, "total_revenue": 0.0}

        product_summary[name]["total_qty"] += qty
        product_summary[name]["total_revenue"] += revenue

    # Filter low-performing products
    low_products = []
    for name, stats in product_summary.items():
        if stats["total_qty"] < threshold:
            low_products.append((name, stats["total_qty"], stats["total_revenue"]))

    # Sort by TotalQuantity ascending (if tie, sort by revenue ascending)
    low_products.sort(key=lambda x: (x[1], x[2]))

    return low_products
