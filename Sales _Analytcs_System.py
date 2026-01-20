from utils.file_handler import read_sales_file
from utils.data_processor import clean_and_validate_data, analyze_sales
from utils.api_handler import fetch_product_info
from utils.data_processor import parse_transactions
from utils.file_handler import read_sales_data

def main():
    file_path = "data/sales_data.txt"
    sales_data = read_sales_file(file_path)

    print("Total records read:", len(sales_data))

    for records in sales_data[:5]:  # Print first 5 records for verification
        print(records)

    raw= read_sales_file("data/sales_data.txt")
    clean_data = parse_transactions(raw)

    print("Parsed records:", len(clean_data))
    print(clean_data[0])

    valid_records = clean_and_validate_data(raw)

    enriched_data = []
    for record in valid_records:
        product_info = fetch_product_info(record["ProductID"])
        record.update(product_info)
        enriched_data.append(record)

    analyze_sales(enriched_data)

if _name_ == "_main_":
    main()