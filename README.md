# FreshMart Data Platform

An end-to-end retail data engineering project built to simulate how customer, product, inventory, cart, and order data can move from operational sources into a cloud analytics platform.

The project demonstrates data generation, validation, event-driven processing, data lake organization, Parquet transformation, metadata management, SQL analytics, and API-based application integration.

---

## Project Overview

FreshMart is a fictional online grocery retailer.

The goal of this project was to build a production-style data pipeline for retail datasets including:

- Customers
- Products
- Inventory
- Carts
- Cart Items
- Orders
- Order Items

The project started with small test datasets and was later scaled to thousands of related records while preserving relationships between customers, products, carts, and orders.

---

## Architecture

```mermaid
flowchart LR
    A[Python Data Generators] --> B[S3 Raw Layer]

    B --> C[S3 Event]
    C --> D[Generic Validation Lambda]

    D --> E[S3 Validated Layer]

    E --> F[S3 Event]
    F --> G[Generic Curator Lambda]

    G --> H[Parquet + Snappy]
    H --> I[S3 Curated Layer]

    G --> J[AWS Glue Data Catalog]
    J --> K[Amazon Athena]

    K --> L[SQL Analytics]

    M[DynamoDB] --> N[Products API Lambda]
    N --> O[API Gateway]
    O --> P[FreshMart Frontend]