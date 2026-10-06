DATASETS = {
    "customers": {
        "required_fields": [
            "customer_id",
            "customer_number",
            "first_name",
            "last_name",
            "email",
            "created_at"
        ],
        "string_fields": [
            "customer_id",
            "customer_number",
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "state",
            "zip_code"
        ],
        "uuid_fields": [
            "customer_id"
        ],
        "email_fields": [
            "email"
        ],
        "timestamp_fields": [
            "created_at"
        ],
        "primary_key": "customer_id",
        "business_key": "customer_number",
        "raw_format": "csv",
        "curated_format": "parquet"
    },

    "products": {
        "required_fields": [
            "product_id",
            "product_number",
            "product_name",
            "category",
            "unit",
            "price",
            "is_active",
            "created_at"
        ],
        "string_fields": [
            "product_id",
            "product_number",
            "product_name",
            "category",
            "unit"
        ],
        "uuid_fields": [
            "product_id"
        ],
        "decimal_fields": [
            "price"
        ],
        "boolean_fields": [
            "is_active"
        ],
        "timestamp_fields": [
            "created_at"
        ],
        "primary_key": "product_id",
        "business_key": "product_number",
        "raw_format": "csv",
        "curated_format": "parquet"
    },

    "inventory": {
        "required_fields": [
            "inventory_id",
            "product_id",
            "quantity_on_hand",
            "reorder_level",
            "updated_at"
        ],
        "string_fields": [
            "inventory_id",
            "product_id"
        ],
        "uuid_fields": [
            "inventory_id",
            "product_id"
        ],
        "integer_fields": [
            "quantity_on_hand",
            "reorder_level"
        ],
        "timestamp_fields": [
            "updated_at"
        ],
        "primary_key": "inventory_id",
        "business_key": "product_id",
        "raw_format": "csv",
        "curated_format": "parquet"
    },

    "carts": {
        "required_fields": [
            "cart_id",
            "customer_id",
            "cart_status",
            "created_at",
            "updated_at"
        ],
        "string_fields": [
            "cart_id",
            "customer_id",
            "cart_status"
        ],
        "uuid_fields": [
            "cart_id",
            "customer_id"
        ],
        "timestamp_fields": [
            "created_at",
            "updated_at"
        ],
        "primary_key": "cart_id",
        "business_key": None,
        "raw_format": "csv",
        "curated_format": "parquet"
    },

    "cart_items": {
        "required_fields": [
            "cart_item_id",
            "cart_id",
            "product_id",
            "quantity",
            "unit_price",
            "added_at"
        ],
        "string_fields": [
            "cart_item_id",
            "cart_id",
            "product_id"
        ],
        "uuid_fields": [
            "cart_item_id",
            "cart_id",
            "product_id"
        ],
        "integer_fields": [
            "quantity"
        ],
        "decimal_fields": [
            "unit_price"
        ],
        "timestamp_fields": [
            "added_at"
        ],
        "primary_key": "cart_item_id",
        "business_key": None,
        "raw_format": "csv",
        "curated_format": "parquet"
    },

    "orders": {
        "required_fields": [
            "order_id",
            "order_number",
            "customer_id",
            "order_status",
            "subtotal",
            "discount_amount",
            "order_total",
            "created_at"
        ],
        "string_fields": [
            "order_id",
            "order_number",
            "customer_id",
            "order_status",
            "promo_code"
        ],
        "uuid_fields": [
            "order_id",
            "customer_id"
        ],
        "decimal_fields": [
            "subtotal",
            "discount_amount",
            "order_total"
        ],
        "timestamp_fields": [
            "created_at"
        ],
        "primary_key": "order_id",
        "business_key": "order_number",
        "raw_format": "csv",
        "curated_format": "parquet"
    },

    "order_items": {
        "required_fields": [
            "order_item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "line_total"
        ],
        "string_fields": [
            "order_item_id",
            "order_id",
            "product_id"
        ],
        "uuid_fields": [
            "order_item_id",
            "order_id",
            "product_id"
        ],
        "integer_fields": [
            "quantity"
        ],
        "decimal_fields": [
            "unit_price",
            "line_total"
        ],
        "timestamp_fields": [],
        "primary_key": "order_item_id",
        "business_key": None,
        "raw_format": "csv",
        "curated_format": "parquet"
    }
}