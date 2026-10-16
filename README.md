# E-Commerce End-to-End Data Engineering Project

## Overview

An end-to-end data engineering project that builds an e-commerce analytics pipeline using Python, Pandas, and PostgreSQL. The pipeline generates sample data, ingests CSV files, transforms and validates data, loads a dimensional data warehouse, and runs SQL analytics to support business decisions.

## Architecture

```text
Sample CSV Data
      |
      v
Python Data Ingestion
      |
      v
Data Transformation
      |
      v
Data Quality Validation
      |
      v
PostgreSQL Data Warehouse
      |
      v
SQL Analytics
      |
      v
Power BI Dashboard (Planned)
```

## Technology Stack

- **Language:** Python, SQL
- **Data Processing:** Pandas
- **Database:** PostgreSQL
- **Connectivity:** psycopg2, python-dotenv
- **Development:** VS Code, Git
- **Visualization:** Power BI (planned)

## Pipeline Features

- Generates sample e-commerce customers, products, orders, order items, and payment data.
- Ingests CSV files into timestamped raw-data batches.
- Transforms order and item data into analytics-ready datasets.
- Runs automated data-quality checks.
- Loads a dimensional warehouse using customer, product, date, and location dimensions and a sales fact table.
- Uses SQL to analyze revenue, orders, product performance, customer performance, and location performance.

## Data Warehouse

| Table | Rows in Current Load |
|---|---:|
| `dim_customer` | 100 |
| `dim_product` | 50 |
| `dim_date` | 263 |
| `dim_location` | 8 |
| `fact_sales` | 1,206 |

The fact table contains 1,206 sales line items across 471 non-cancelled orders.

## Data Quality

The latest completed validation run passed **38 checks**, with zero failed checks and zero warnings.

## SQL Analytics

The SQL analytics file is located at `sql/analytics/analytics.sql` and includes:

1. Overall business KPIs
2. Monthly revenue trends
3. Top 10 products by revenue
4. Top 10 customers by revenue
5. Revenue by location

## Project Structure

```text
ecommerce-data-engineering/
├── data/
│   ├── sample/
│   ├── raw/
│   └── processed/
├── sql/
│   ├── analytics/
│   ├── dimensions/
│   ├── facts/
│   └── staging/
├── src/
│   ├── ingestion/
│   ├── transformation/
│   ├── validation/
│   └── warehouse/
├── tests/
├── config/
├── airflow/
├── docker/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd ecommerce-data-engineering
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and set your local PostgreSQL credentials.

**Never commit `.env` or publish database passwords.**

### 5. Create the database

Create a PostgreSQL database named `ecommerce_dw`, then execute the project's warehouse schema SQL scripts before loading data.

### 6. Run the pipeline

Run the data-generation, ingestion, transformation, validation, and warehouse-loading scripts in the order documented in the project.

## Current Status

- [x] Sample data generation
- [x] Data ingestion
- [x] Data transformation
- [x] Data quality validation
- [x] PostgreSQL warehouse loading
- [x] SQL analytics
- [ ] Power BI dashboard
- [ ] GitHub publication and screenshots

## Future Improvements

- Build an interactive Power BI dashboard.
- Orchestrate the pipeline with Apache Airflow.
- Containerize services with Docker.
- Add automated tests and CI/CD.
- Explore cloud storage and a cloud data warehouse.

## Disclaimer

This project uses synthetic sample data for educational and portfolio purposes. The dataset does not represent actual company sales or customers.
