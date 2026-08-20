import pandas as pd
from sqlalchemy import create_engine

# 1. Load the processed data from your local directory
df_cust = pd.read_parquet("data/raw/customers.parquet")
df_txn = pd.read_parquet("data/processed/model_ready_data.parquet")

# 2. Create SQL Server connection 
server = r'HARIOM\SQLEXPRESS'
database = 'master'
driver = 'ODBC Driver 17 for SQL Server' 

connection_string = f"mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes"
engine = create_engine(connection_string)

print("Loading dim_customer...")
# (Optional: You can comment out the line below if dim_customer is already loaded so it doesn't duplicate)
# df_cust.to_sql('dim_customer', con=engine, if_exists='append', index=False)

print("Transforming and Loading fact_transaction...")

# --- NEW FIX: Align DataFrame with SQL Schema ---
# Rename 'timestamp' to match SQL DDL
df_txn.rename(columns={'timestamp': 'txn_timestamp'}, inplace=True)

# Define the exact columns expected by the fact_transaction table
fact_columns = [
    'txn_id', 'customer_id', 'amount_inr', 'txn_timestamp', 
    'payment_method', 'txn_count_1hr', 'amt_spent_1hr', 
    'amount_z_score', 'is_fraud'
]

# Filter the dataframe to drop all other columns (like state, merchant_category, etc.)
df_txn_final = df_txn[fact_columns]
# ------------------------------------------------

# Push filtered data to SQL Server
df_txn_final.to_sql('fact_transaction', con=engine, if_exists='append', index=False)

print("Data successfully loaded into SQL Server!")