import psycopg2
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

def db_run_query(query,params=None):
    try:
        # Connection setup
        connection = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", 6543),
            dbname=os.getenv("DB_NAME", "postgres")
        )
        
        # Run query into DataFrame
        df = pd.read_sql(query, connection, params=params)
        
        return df
    
    except Exception as e:
        print(f"Query failed: {e}")
        return pd.DataFrame()  # return empty df if error
    
    finally:
        if 'connection' in locals() and connection:
            connection.close()