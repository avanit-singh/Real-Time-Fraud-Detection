📌 Project Overview
This is a comprehensive, end-to-end data engineering and analytics project focused on Real-time Fraud Detection for the Indian Fintech sector. India processes billions of digital transactions monthly, driven primarily by UPI, RuPay cards, and IMPS/NEFT. With this massive scale comes a surge in sophisticated fraud, making this project highly relevant for balancing high-speed fraud detection with regulatory compliance.

🏗️ Architecture & Tech Stack
Data Generation (Python): Generates a synthetic dataset that mimics transaction behavior. PII like names and actual phone numbers are masked using one-way hashing to comply with the DPDP Act.
Data Processing (PySpark): Leverages PySpark ETL to engineer "velocity features" (e.g., number of transactions in the last hour) based on user behavior.
Data Warehouse (SQL Server): Uses a Star Schema containing Dimension and Fact tables to store processed data for reporting.
Machine Learning (Scikit-Learn): Compares a hard-coded rule-based engine against a Random Forest classifier. The ML approach catches twice as much fraud (89.5% recall) and significantly reduces false alarms (0.8% FPR), meaning fewer blocked cards and happier Indian customers.
Analytics (Power BI): Features a "Fraud Command Center" dashboard built to present findings to Indian stakeholders. It uses DAX measures to highlight geographic fraud hotspots and break down financial loss by payment method.

🚀 Setup & Execution
Step 1: Run scripts/01_data_generation.py to execute the Python script to generate realistic Indian txn data.
Step 2: Run scripts/02_pyspark_etl.py to execute feature engineering and data cleaning.
Step 3: Deploy the star schema creation by running sql/01_ddl_schema.sql in your SQL Data Warehouse.
Step 4: Execute the database loading script to populate the tables.
Step 5: Open dashboards/Fraud_Command_Center.pbix (the Power BI Dashboard file) to interact with the visualizations.

📈 Scaling, Cost, & Validation Considerations
Scalability: In a true production environment, switch PySpark batch processing to Spark Structured Streaming reading from Apache Kafka for sub-second latency.
Cost Management: Utilize AWS Spot Instances or GCP Preemptible VMs for PySpark ETL jobs.
Data Validation: Implement Great Expectations in the pipeline to ensure amount_inr is never negative and is_fraud is strictly boolean before models train.
