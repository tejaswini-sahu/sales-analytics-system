from utils.api_handler import *
from utils.data_processor import *
from utils.file_handler import *
def main():
    """
    Main execution function (end-to-end workflow)
    """
    try:
        print("=" * 40)
        print("SALES ANALYTICS SYSTEM")
        print("=" * 40)
        print()

        # ---------------- [1/10] READ FILE ----------------
        print("[1/10] Reading sales data...")
        raw_lines = read_sales_data("data\sales_data.txt")
        if not raw_lines:
            print("✗ Failed to read sales data. Please check file path/encoding.")
            return
        print(f"✓ Successfully read {len(raw_lines)} transactions\n")

        # ---------------- [2/10] PARSE + CLEAN ----------------
        print("[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(transactions)} records\n")

        if not transactions:
            print("✗ No transactions parsed. Exiting.")
            return

        # ---------------- [3/10] FILTER OPTIONS ----------------
        print("[3/10] Filter Options Available:")

        # show regions + amount range BEFORE asking
        regions_available = sorted(set(t["Region"] for t in transactions if t.get("Region")))
        amounts = [(t["Quantity"] * t["UnitPrice"]) for t in transactions if "Quantity" in t and "UnitPrice" in t]

        print("Regions:", ", ".join(regions_available) if regions_available else "None")

        if amounts:
            print(f"Amount Range: ₹{min(amounts):,.0f} - ₹{max(amounts):,.0f}")
        else:
            print("Amount Range: Not available")

        choice = input("\nDo you want to filter data? (y/n): ").strip().lower()
        selected_region = None
        min_amount = None
        max_amount = None

        if choice == "y":
            # region filter
            selected_region = input("Enter region (or press Enter to skip): ").strip()
            if selected_region == "":
                selected_region = None

            # amount filters
            min_in = input("Enter minimum amount (or press Enter to skip): ").strip()
            max_in = input("Enter maximum amount (or press Enter to skip): ").strip()

            if min_in != "":
                try:
                    min_amount = float(min_in.replace(",", ""))
                except ValueError:
                    print("Invalid min amount entered. Skipping min filter.")
                    min_amount = None

            if max_in != "":
                try:
                    max_amount = float(max_in.replace(",", ""))
                except ValueError:
                    print("Invalid max amount entered. Skipping max filter.")
                    max_amount = None

        print()

        # ---------------- [4/10] VALIDATE + APPLY FILTERS ----------------
        print("[4/10] Validating transactions...")
        valid_transactions, invalid_count, summary = validate_and_filter(
            transactions,
            region=selected_region,
            min_amount=min_amount,
            max_amount=max_amount
        )
        print(f"✓ Valid: {len(valid_transactions)} | Invalid: {invalid_count}\n")

        if not valid_transactions:
            print("✗ No valid transactions left after validation/filtering. Exiting.")
            return

        # ---------------- [5/10] ANALYSIS ----------------
        print("[5/10] Analyzing sales data...")

        total_rev = calculate_total_revenue(valid_transactions)
        region_stats = region_wise_sales(valid_transactions)
        top_products = top_selling_products(valid_transactions, n=5)
        customers = customer_analysis(valid_transactions)
        daily_trend = daily_sales_trend(valid_transactions)
        peak_day = find_peak_sales_day(valid_transactions)
        low_products = low_performing_products(valid_transactions, threshold=10)

        print("✓ Analysis complete\n")

        # ---------------- [6/10] FETCH API PRODUCTS ----------------
        print("[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        if not api_products:
            print("✗ API fetch failed. Continuing without enrichment.\n")
            product_mapping = {}
        else:
            print(f"✓ Fetched {len(api_products)} products\n")
            product_mapping = create_product_mapping(api_products)

        # ---------------- [7/10] ENRICH DATA ----------------
        print("[7/10] Enriching sales data...")
        enriched_transactions = enrich_sales_data(valid_transactions, product_mapping)

        enriched_success = sum(1 for t in enriched_transactions if t.get("API_Match") is True)
        total_enriched = len(enriched_transactions)
        success_rate = (enriched_success / total_enriched * 100) if total_enriched > 0 else 0.0

        print(f"✓ Enriched {enriched_success}/{total_enriched} transactions ({success_rate:.1f}%)\n")

        # ---------------- [8/10] SAVE ENRICHED FILE ----------------
        print("[8/10] Saving enriched data...")
        save_enriched_data(enriched_transactions, filename="data/enriched_sales_data.txt")
        print("✓ Saved to: data/enriched_sales_data.txt\n")

        # ---------------- [9/10] GENERATE REPORT ----------------
        print("[9/10] Generating report...")
        generate_sales_report(valid_transactions, enriched_transactions, output_file="output/sales_report.txt")
        print("✓ Report saved to: output/sales_report.txt\n")

        # ---------------- [10/10] DONE ----------------
        print("[10/10] Process Complete!")
        print("=" * 40)
        print("Files generated:")
        print(" - data/enriched_sales_data.txt")
        print(" - output/sales_report.txt")
        print("=" * 40)

    except Exception as e:
        print("\n✗ Something went wrong!")
        print("Error:", str(e))
        print("Please check your input files and try again.")


if __name__ == "__main__":
    main()
