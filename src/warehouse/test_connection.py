
import os
import psycopg2
from dotenv import load_dotenv

# Load credentials from the project root .env file
load_dotenv()

try:
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
    )

    print("SUCCESS: Connected to PostgreSQL!")
    print(f"Database: {connection.info.dbname}")

    connection.close()
    print("Connection closed successfully.")

except psycopg2.OperationalError as error:
    print("ERROR: Could not connect to PostgreSQL.")
    print("Check your .env settings and ensure PostgreSQL is running.")
    print(f"Details: {error}")
