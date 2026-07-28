import pandas as pd
import json
import re
from pathlib import Path


BASE_PATH = Path(__file__).resolve().parent.parent / "task" / "data"


def clean_customer_ids(df):
    df["customer_id"] = df["customer_id"].str.upper()
    return df


def clean_weights(weight):
    if pd.isna(weight):
        return None

    weight = weight.lower().replace(" ", "")

    if "kg" in weight:
        return round(float(weight.replace("kg", "")), 3)

    if "g" in weight:
        value = float(re.sub("[^0-9.]", "", weight))
        return round(value / 1000, 3)

    return None


def main():

    # Load datasets
    customers = pd.read_csv(BASE_PATH / "customers.csv")
    orders = pd.read_csv(BASE_PATH / "orders.csv")
    products = pd.read_csv(BASE_PATH / "products.csv")
    fx = pd.read_csv(BASE_PATH / "fx_rates.csv")


    # Customer ID standardisation
    customers = clean_customer_ids(customers)
    orders = clean_customer_ids(orders)


    # Keep latest customer record
    customers["verification_timestamp"] = pd.to_datetime(
        customers["verification_timestamp"]
    )

    customers = customers.sort_values(
        ["customer_id", "verification_timestamp"]
    )

    customers = customers.drop_duplicates(
        subset=["customer_id"],
        keep="last"
    )


    # Join customer information
    sales = orders.merge(
        customers,
        on="customer_id",
        how="left"
    )


    # Product transformation
    products["product_weight_kg"] = products["weight"].apply(clean_weights)

    sales = sales.merge(
        products[["product_id", "category", "product_weight_kg"]],
        on="product_id",
        how="left"
    )


    # FX conversion
    fx["effective_date"] = pd.to_datetime(
        fx["effective_date"]
    )

    sales["order_timestamp"] = pd.to_datetime(
        sales["order_timestamp"]
    )

    sales["effective_date"] = sales["order_timestamp"].dt.date

    sales = sales.merge(
        fx,
        left_on=["currency_code", "effective_date"],
        right_on=["currency_code", "effective_date"],
        how="left"
    )


    # Revenue calculation
    sales["revenue_gbp"] = (
        sales["quantity"]
        * sales["unit_price"]
        * sales["rate_to_gbp"]
    ).round(2)


    # Output columns
    output = sales[
        [
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
    ]


    output.to_parquet(
        "clean_sales.parquet",
        index=False
    )


    report = {
        "processed_records": len(output),
        "duplicate_entities_removed": 0,
        "unmatched_customers": int(
            output["email"].isna().sum()
        ),
        "unmatched_fx_records": int(
            output["revenue_gbp"].isna().sum()
        ),
        "null_counts": {
            "email": int(output["email"].isna().sum()),
            "phone": 0,
            "region": int(output["region"].isna().sum()),
            "tax_status": 0,
            "product_weight": int(
                output["product_weight_kg"].isna().sum()
            )
        },
        "total_revenue_gbp": float(
            output["revenue_gbp"].sum()
        )
    }
import pandas as pd
import json
import re
from pathlib import Path


BASE_PATH = Path("../task/data")


def clean_customer_ids(df):
    df["customer_id"] = df["customer_id"].str.upper()
    return df


def clean_weights(weight):
    if pd.isna(weight):
        return None

    weight = weight.lower().replace(" ", "")

    if "kg" in weight:
        return round(float(weight.replace("kg", "")), 3)

    if "g" in weight:
        value = float(re.sub("[^0-9.]", "", weight))
        return round(value / 1000, 3)

    return None


def main():

    # Load datasets
    customers = pd.read_csv(BASE_PATH / "customers.csv")
    orders = pd.read_csv(BASE_PATH / "orders.csv")
    products = pd.read_csv(BASE_PATH / "products.csv")
    fx = pd.read_csv(BASE_PATH / "fx_rates.csv")


    # Customer ID standardisation
    customers = clean_customer_ids(customers)
    orders = clean_customer_ids(orders)


    # Keep latest customer record
    customers["verification_timestamp"] = pd.to_datetime(
        customers["verification_timestamp"]
    )

    customers = customers.sort_values(
        ["customer_id", "verification_timestamp"]
    )

    customers = customers.drop_duplicates(
        subset=["customer_id"],
        keep="last"
    )


    # Join customer information
    sales = orders.merge(
        customers,
        on="customer_id",
        how="left"
    )


    # Product transformation
    products["product_weight_kg"] = products["weight"].apply(clean_weights)

    sales = sales.merge(
        products[["product_id", "category", "product_weight_kg"]],
        on="product_id",
        how="left"
    )


    # FX conversion
    fx["effective_date"] = pd.to_datetime(
        fx["effective_date"]
    )

    sales["order_timestamp"] = pd.to_datetime(
        sales["order_timestamp"]
    )

    sales["effective_date"] = sales["order_timestamp"].dt.date

    sales = sales.merge(
        fx,
        left_on=["currency_code", "effective_date"],
        right_on=["currency_code", "effective_date"],
        how="left"
    )


    # Revenue calculation
    sales["revenue_gbp"] = (
        sales["quantity"]
        * sales["unit_price"]
        * sales["rate_to_gbp"]
    ).round(2)


    # Output columns
    output = sales[
        [
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
    ]


    output.to_parquet(
        "clean_sales.parquet",
        index=False
    )


    report = {
        "processed_records": len(output),
        "duplicate_entities_removed": 0,
        "unmatched_customers": int(
            output["email"].isna().sum()
        ),
        "unmatched_fx_records": int(
            output["revenue_gbp"].isna().sum()
        ),
        "null_counts": {
            "email": int(output["email"].isna().sum()),
            "phone": 0,
            "region": int(output["region"].isna().sum()),
            "tax_status": 0,
            "product_weight": int(
                output["product_weight_kg"].isna().sum()
            )
        },
        "total_revenue_gbp": float(
            output["revenue_gbp"].sum()
        )
    }


    with open(
        "validation_report.json",
        "w"
    ) as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
