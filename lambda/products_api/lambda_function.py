import boto3
import json
from decimal import Decimal

TABLE_NAME = "freshmart-products"

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body, cls=DecimalEncoder)
    }


def lambda_handler(event, context):
    route_key = event.get("routeKey", "")

    if route_key == "GET /products":
        result = table.scan()

        products = [
            item
            for item in result.get("Items", [])
            if item.get("is_active") is True
        ]

        products.sort(
            key=lambda x: x.get("product_number", "")
        )

        return response(
            200,
            {
                "count": len(products),
                "products": products
            }
        )

    if route_key == "GET /products/{product_id}":
        product_id = (
            event.get("pathParameters", {})
            .get("product_id")
        )

        if not product_id:
            return response(
                400,
                {"message": "product_id is required"}
            )

        result = table.get_item(
            Key={
                "product_id": product_id
            }
        )

        product = result.get("Item")

        if not product:
            return response(
                404,
                {"message": "Product not found"}
            )

        return response(
            200,
            product
        )

    return response(
        404,
        {"message": "Route not found"}
    )