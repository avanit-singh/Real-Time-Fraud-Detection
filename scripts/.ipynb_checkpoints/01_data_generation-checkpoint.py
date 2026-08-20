import pandas as pd
import numpy as np
from faker import Faker
import hashlib
from datetime import datetime, timedelta

fake = Faker('en_IN')

# Configuration
NUM_CUSTOMERS = 10000
NUM_TRANSACTIONS = 500000
PAYMENT_METHODS = ['UPI', 'RuPay_Card', 'Visa_Card', 'IMPS']

def hash_pii(data):
    return hashlib.sha256(data.encode()).hexdigest()

print("Generating synthetic customers...")
customers = []
for _ in range(NUM_CUSTOMERS):
    customers.append({
        'customer_id': hash_pii(fake.phone_number()), # Masked
        'state': fake.state(),
        'account_age_days': np.random.randint(1, 3650)
    })
df_customers = pd.DataFrame(customers)

print("Generating synthetic transactions...")
transactions = []
start_date = datetime.now() - timedelta(days=30)

for _ in range(NUM_TRANSACTIONS):
    is_fraud = np.random.choice([0, 1], p=[0.98, 0.02]) # 2% base fraud rate
    amount = np.random.exponential(1500) if not is_fraud else np.random.uniform(50000, 200000)
    
    transactions.append({
        'txn_id': fake.uuid4(),
        'customer_id': np.random.choice(df_customers['customer_id']),
        'amount_inr': round(amount, 2),
        'timestamp': fake.date_time_between(start_date=start_date, end_date='now'),
        'payment_method': np.random.choice(PAYMENT_METHODS),
        'merchant_category': fake.bs(),
        'is_fraud': is_fraud
    })

df_transactions = pd.DataFrame(transactions)
df_transactions.to_parquet('data/raw/transactions.parquet', index=False)
df_customers.to_parquet('data/raw/customers.parquet', index=False)
print("Data generation complete.")