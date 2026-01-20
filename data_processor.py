mport os
import re

def clean_and_validate_data(raw_records):
    total_parsed = 0
    invalid = 0
    valid_data = []

    for line in raw_records:
        total_parsed += 1

        try:
            parts = line.split("|")
            if len(parts) < 8:
                invalid += 1
                continue

            transaction_id = parts[0].strip()
            date = parts[1].strip()
            product_id = parts[2].strip()
            product_name = parts[3].replace(",", "").strip()
            quantity = int(parts[4].replace(",", ""))
            unit_price = float(parts[5].replace(",", ""))
            customer_id = parts[6].strip()
            region = parts[7].strip()

            # Validation Rules
            if not transaction_id.startswith("T"):
                invalid += 1
                continue

            if quantity <= 0 or unit_price <= 0:
                invalid += 1
                continue
            
            if not customer_id or not region:
                invalid += 1
                continue

            valid_data.append({
                "TransactionID": transaction_id,
                "Date": date,
                "ProductID": product_id,
                "ProductName": product_name,
                "Quantity": quantity,
                "UnitPrice": unit_price,
                "CustomerID": customer_id,
                "Region": region
            })

        except:
            invalid += 1

    print(f"Total records parsed: {total_parsed}")
    print(f"Invalid records removed: {invalid}")
    print(f"Valid records after cleaning: {len(valid_data)}")

    return valid_data


def analyze_sales(enriched_data):

    os.makedirs("outputs", exist_ok=True)
    total_revenue = 0
    region_sales = {}

    for record in enriched_data:
        revenue = record["Quantity"] * record["UnitPrice"]
        total_revenue += revenue
        region_sales[record["Region"]] = region_sales.get(record["Region"], 0) + revenue

    with open("outputs/sales_report.txt", "w") as f:
        f.write("Sales Report\n")
        f.write(f"Total Revenue: {total_revenue}\n")
        f.write("Revenue by Region:\n")
        for region, revenue in region_sales.items():
            f.write(f"{region}: {revenue}\n")

    print("Sales report generated successfully.")

def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries
    """

    transactions = []

    for line in raw_lines:
        # Split by pipe delimiter
        parts = line.split("|")

        # Skip rows with incorrect number of fields
        if len(parts) != 8:
            continue

        try:
            transaction = {
                "TransactionID": parts[0].strip(),
                "Date": parts[1].strip(),
                "ProductID": parts[2].strip(),

                # Remove commas from ProductName
                "ProductName": parts[3].replace(",", "").strip(),

                # Remove commas and convert to int
                "Quantity": int(parts[4].replace(",", "")),

                # Remove commas and convert to float
                "UnitPrice": float(parts[5].replace(",", "")),

                "CustomerID": parts[6].strip(),
                "Region": parts[7].strip()
            }

            transactions.append(transaction)

        except ValueError:
            # Skip rows with conversion issues
            continue

    return transactions

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters
    """

    valid_transactions = []
    invalid_count = 0

    # Collect info for display
    regions = set()
    amounts = []

    for tx in transactions:
        # Required fields check
        required_fields = [
            "TransactionID", "Date", "ProductID", "ProductName",
            "Quantity", "UnitPrice", "CustomerID", "Region"
        ]

        if not all(field in tx for field in required_fields):
            invalid_count += 1
            continue

        # Validation rules
        if not tx["TransactionID"].startswith("T"):
            invalid_count += 1
            continue

        if not tx["ProductID"].startswith("P"):
            invalid_count += 1
            continue

        if not tx["CustomerID"].startswith("C"):
            invalid_count += 1
            continue

        if tx["Quantity"] <= 0 or tx["UnitPrice"] <= 0:
            invalid_count += 1
            continue

        amount = tx["Quantity"] * tx["UnitPrice"]
        tx["Amount"] = amount  # useful for filtering

        regions.add(tx["Region"])
        amounts.append(amount)

        valid_transactions.append(tx)

    # Display available options
    print("Available Regions:", ", ".join(sorted(regions)))
    if amounts:
        print(f"Transaction Amount Range: {min(amounts)} - {max(amounts)}")

    # Filtering
    filtered_by_region = 0
    filtered_by_amount = 0

    filtered_transactions = valid_transactions

    if region:
        before = len(filtered_transactions)
        filtered_transactions = [
            tx for tx in filtered_transactions if tx["Region"] == region
        ]
        filtered_by_region = before - len(filtered_transactions)
        print(f"After region filter ({region}): {len(filtered_transactions)}")

    if min_amount is not None or max_amount is not None:
        before = len(filtered_transactions)
        filtered_transactions = [
            tx for tx in filtered_transactions
            if (min_amount is None or tx["Amount"] >= min_amount)
            and (max_amount is None or tx["Amount"] <= max_amount)
        ]
        filtered_by_amount = before - len(filtered_transactions)
        print(f"After amount filter: {len(filtered_transactions)}")

    summary = {
        "total_input": len(transactions),
        "invalid": invalid_count,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(filtered_transactions)
    }

    return filtered_transactions, invalid_count, summary