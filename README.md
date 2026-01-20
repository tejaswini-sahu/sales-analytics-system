# Sales Analytics System

This project reads raw sales transaction data from a pipe-delimited text file, cleans and validates it, optionally filters it, performs multiple sales analytics, enriches transactions using the DummyJSON Products API, saves enriched data to a new file, and finally generates a detailed sales report.

---

## Project Structure

```
project/
│
├── main.py
├── data/
│   ├── sales_data.txt
│   └── enriched_sales_data.txt        (generated)
│
├── output/
│   └── sales_report.txt               (generated)
│
└── utils/
    ├── file_handler.py
    ├── data_processor.py
    └── api_handler.py
```

---

## What This Program Does (Workflow)

When you run the program, it follows these steps:

### **[1/10] Read Sales Data**
- Reads the file: `data/sales_data.txt`
- Handles encoding issues automatically
- Removes header and empty lines

✔ Output Example:
```
[1/10] Reading sales data...
✓ Successfully read 80 transactions
```

---

### **[2/10] Parse & Clean Transactions**
- Splits each row using pipe delimiter `|`
- Converts:
  - `Quantity` → integer
  - `UnitPrice` → float
- Removes commas from numbers like `1,500 → 1500`
- Cleans commas inside product names like `Mouse,Wireless → Mouse Wireless`
- Skips rows with incorrect number of fields

✔ Output Example:
```
[2/10] Parsing and cleaning data...
✓ Parsed 80 records
```

---

### **[3/10] Display Filter Options**
The program shows:
- Available regions
- Transaction amount range (Quantity × UnitPrice)

Then it asks the user:

```
Do you want to filter data? (y/n):
```

If user selects **y**, it allows filtering by:
- Region (example: North)
- Minimum transaction amount
- Maximum transaction amount

---

### **[4/10] Validate & Filter Transactions**
The program removes invalid transactions using rules like:
- Quantity must be > 0
- UnitPrice must be > 0
- TransactionID must start with **T**
- ProductID must start with **P**
- CustomerID must start with **C**
- CustomerID and Region must not be empty

✔ Output Example:
```
[4/10] Validating transactions...
✓ Valid: 70 | Invalid: 10
```

---

### **[5/10] Perform Sales Analysis**
The system calculates:
- Total revenue
- Region-wise sales
- Top selling products
- Customer spending patterns
- Daily sales trend
- Peak sales day
- Low performing products

✔ Output Example:
```
[5/10] Analyzing sales data...
✓ Analysis complete
```

---

### **[6/10] Fetch Products from DummyJSON API**
The program calls:

```
https://dummyjson.com/products?limit=100
```

It fetches product details like:
- Title
- Category
- Brand
- Rating

✔ Output Example:
```
[6/10] Fetching product data from API...
✓ Fetched 100 products
```

If the API fails, the program continues without enrichment.

---

### **[7/10] Enrich Sales Data**
Each transaction is enriched using API product mapping by matching:

`ProductID = P101 → API Product ID = 101`

New fields added:
- `API_Category`
- `API_Brand`
- `API_Rating`
- `API_Match` (True/False)

✔ Output Example:
```
[7/10] Enriching sales data...
✓ Enriched 60/70 transactions (85.7%)
```

---

### **[8/10] Save Enriched Data**
The enriched output is saved to:

`data/enriched_sales_data.txt`

Format:
```
TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region|API_Category|API_Brand|API_Rating|API_Match
```

✔ Output Example:
```
[8/10] Saving enriched data...
✓ Saved to: data/enriched_sales_data.txt
```

---

### **[9/10] Generate Sales Report**
A detailed report is generated at:

`output/sales_report.txt`

The report includes:
1. Header
2. Overall Summary
3. Region Performance
4. Top Products
5. Top Customers
6. Daily Trend
7. Product Performance
8. API Enrichment Summary

✔ Output Example:
```
[9/10] Generating report...
✓ Report saved to: output/sales_report.txt
```

---

### **[10/10] Process Complete**
Finally, the program prints:

```
[10/10] Process Complete!
Files generated:
 - data/enriched_sales_data.txt
 - output/sales_report.txt
```

---

## How to Run the Project

### Install Required Library
This project requires `requests` for API calls:

```bash
pip install requests
```

---

### Run the Program
Make sure your file exists at:

`data/sales_data.txt`

Then run:

```bash
python main.py
```

---

## Output Files Generated

| File | Description |
|------|------------|
| `data/enriched_sales_data.txt` | Cleaned + enriched transaction data |
| `output/sales_report.txt` | Full formatted sales analytics report |

---

## Error Handling

This program is designed not to crash.

It handles:
- Missing file errors (`FileNotFoundError`)
- Encoding errors (tries `utf-8`, `latin-1`, `cp1252`)
- Invalid transaction rows
- API connection failures

If something goes wrong, you will see a friendly message like:

```
✗ Something went wrong!
Error: ...
Please check your input files and try again.
```

---

## Notes

- Filtering is optional.
- Enrichment depends on matching numeric Product IDs with DummyJSON product IDs.
- If the API does not contain a matching product, `API_Match = False`.

---

