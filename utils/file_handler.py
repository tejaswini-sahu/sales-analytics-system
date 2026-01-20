
def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues

    Returns: list of raw lines (strings)

    Expected Output Format:
    ['T001|2024-12-01|P101|Laptop|2|45000|C001|North', ...]

    Requirements:
    - Use 'with' statement
    - Handle different encodings (try 'utf-8', 'latin-1', 'cp1252')
    - Handle FileNotFoundError with appropriate error message
    - Skip the header row
    - Remove empty lines
    """
    encodings_to_try = ["utf-8", "latin-1", "cp1252"]

    for enc in encodings_to_try:
        try:
            with open(filename, "r", encoding=enc) as f:
                lines = f.readlines()

            # Remove empty lines + strip newline spaces
            lines = [line.strip() for line in lines if line.strip()]

            # Skip header row (first line)
            if lines:
                lines = lines[1:]

            return lines

        except UnicodeDecodeError:
            # Try next encoding
            continue

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []

    # If all encodings fail
    print(f"Error: Could not read file '{filename}' due to encoding issues.")
    return []

def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries

    Returns: list of dictionaries with keys:
    ['TransactionID', 'Date', 'ProductID', 'ProductName',
     'Quantity', 'UnitPrice', 'CustomerID', 'Region']

    Requirements:
    - Split by pipe delimiter '|'
    - Handle commas within ProductName (remove or replace)
    - Remove commas from numeric fields and convert to proper types
    - Convert Quantity to int
    - Convert UnitPrice to float
    - Skip rows with incorrect number of fields
    """
    transactions = []
    expected_fields = 8

    for line in raw_lines:
        if not line or not line.strip():
            continue

        parts = line.strip().split("|")

        # Skip incorrect number of fields
        if len(parts) != expected_fields:
            continue

        transaction_id = parts[0].strip()
        date = parts[1].strip()
        product_id = parts[2].strip()
        product_name = parts[3].strip()
        quantity_raw = parts[4].strip()
        unit_price_raw = parts[5].strip()
        customer_id = parts[6].strip()
        region = parts[7].strip()

        # Handle commas in ProductName (remove commas or replace with space)
        # Example: "Mouse,Wireless" -> "Mouse Wireless"
        product_name = product_name.replace(",", " ").strip()

        # Handle commas in numeric fields (e.g., "1,500" -> "1500")
        quantity_raw = quantity_raw.replace(",", "")
        unit_price_raw = unit_price_raw.replace(",", "")

        # Convert to correct types
        try:
            quantity = int(quantity_raw)
            unit_price = float(unit_price_raw)
        except ValueError:
            continue

        transactions.append({
            "TransactionID": transaction_id,
            "Date": date,
            "ProductID": product_id,
            "ProductName": product_name,
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "CustomerID": customer_id,
            "Region": region
        })

    return transactions

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters

    Parameters:
    - transactions: list of transaction dictionaries
    - region: filter by specific region (optional)
    - min_amount: minimum transaction amount (Quantity * UnitPrice) (optional)
    - max_amount: maximum transaction amount (optional)

    Returns: tuple (valid_transactions, invalid_count, filter_summary)
    """
    required_fields = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region"
    ]

    total_input = len(transactions)
    invalid_count = 0
    valid_transactions = []

    # ---------- VALIDATION ----------
    for tx in transactions:
        # Check required fields exist and are not empty/None
        missing = False
        for field in required_fields:
            if field not in tx or tx[field] is None or str(tx[field]).strip() == "":
                missing = True
                break

        if missing:
            invalid_count += 1
            continue

        # ID format checks
        if not str(tx["TransactionID"]).startswith("T"):
            invalid_count += 1
            continue
        if not str(tx["ProductID"]).startswith("P"):
            invalid_count += 1
            continue
        if not str(tx["CustomerID"]).startswith("C"):
            invalid_count += 1
            continue

        # Quantity and UnitPrice rules
        try:
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
        except (ValueError, TypeError):
            invalid_count += 1
            continue

        if qty <= 0 or price <= 0:
            invalid_count += 1
            continue

        valid_transactions.append(tx)

    # ---------- DISPLAY AVAILABLE OPTIONS ----------
    regions_available = sorted(set(t["Region"] for t in valid_transactions if t.get("Region")))
    print("Available Regions:", regions_available)

    # Amount range based on valid transactions
    amounts = [(t["Quantity"] * t["UnitPrice"]) for t in valid_transactions]
    if amounts:
        print(f"Transaction Amount Range: {min(amounts):.2f} to {max(amounts):.2f}")
    else:
        print("Transaction Amount Range: No valid transactions found")

    # ---------- FILTERING ----------
    filtered_by_region = 0
    filtered_by_amount = 0

    filtered = valid_transactions

    # Region filter
    if region:
        before = len(filtered)
        filtered = [t for t in filtered if t.get("Region") == region]
        filtered_by_region = before - len(filtered)
        print(f"After Region Filter ({region}): {len(filtered)} records")

    # Amount filters
    if min_amount is not None or max_amount is not None:
        before = len(filtered)

        def amount_ok(t):
            amt = t["Quantity"] * t["UnitPrice"]
            if min_amount is not None and amt < min_amount:
                return False
            if max_amount is not None and amt > max_amount:
                return False
            return True

        filtered = [t for t in filtered if amount_ok(t)]
        filtered_by_amount = before - len(filtered)

        print(
            f"After Amount Filter (min={min_amount}, max={max_amount}): {len(filtered)} records"
        )

    filter_summary = {
        "total_input": total_input,
        "invalid": invalid_count,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(filtered)
    }

    return filtered, invalid_count, filter_summary
