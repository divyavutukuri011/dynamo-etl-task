import pandas as pd
import json
from pathlib import Path


OUTPUT_FILE = Path("../solution/clean_sales.parquet")
REPORT_FILE = Path("../solution/validation_report.json")


def verify():

    # Check output files exist
    assert OUTPUT_FILE.exists(), "clean_sales.parquet missing"
    assert REPORT_FILE.exists(), "validation_report.json missing"


    # Load parquet
    df = pd.read_parquet(OUTPUT_FILE)


    # Required columns
    required_columns = [
        "order_id",
        "customer_id",
        "order_timestamp",
        "email",
        "region",
        "product_id",
        "category",
        "quantity",
        "unit_price",
        "product_weight_kg",
        "revenue_gbp"
    ]

    for col in required_columns:
        assert col in df.columns, f"Missing column: {col}"


    # Check customer ID format
    assert (
        df["customer_id"]
        .str.isupper()
        .all()
    ), "Customer IDs not uppercase"


    # Check revenue exists
    assert (
        df["revenue_gbp"]
        .notna()
        .all()
    ), "Missing revenue values"


    # Load report
    with open(REPORT_FILE) as f:
        report = json.load(f)


    required_keys = [
        "processed_records",
        "duplicate_entities_removed",
        "unmatched_customers",
        "unmatched_fx_records",
        "null_counts",
        "total_revenue_gbp"
    ]


    for key in required_keys:
        assert key in report, f"Missing report field: {key}"


    assert (
        report["processed_records"]
        == len(df)
    )


    print("Validation Passed")


if __name__ == "__main__":
    verify()

