-- Dimension Tables
CREATE TABLE dim_customer (
    customer_id VARCHAR(256) PRIMARY KEY, -- Hashed PII
    state VARCHAR(100),
    account_age_days INT
);

-- Fact Table
CREATE TABLE fact_transaction (
    txn_id VARCHAR(256) PRIMARY KEY,
    customer_id VARCHAR(256) REFERENCES dim_customer(customer_id),
    amount_inr DECIMAL(15, 2),
    txn_timestamp TIMESTAMP,
    payment_method VARCHAR(50),
    txn_count_1hr INT,
    amt_spent_1hr DECIMAL(15,2),
    amount_z_score DECIMAL(10,4),
    is_fraud INT
);