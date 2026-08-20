import os
os.environ['HADOOP_HOME'] = 'C:\\hadoop'

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, count, sum, avg, expr
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("Raksha_ETL").getOrCreate()

# Load Data
df_txn = spark.read.parquet("data/raw/transactions.parquet")
df_cust = spark.read.parquet("data/raw/customers.parquet")

# Ensure timestamp format
df_txn = df_txn.withColumn("timestamp", col("timestamp").cast("timestamp"))

# Feature Engineering: Time Windowing (Velocity Rules)
# Calculate number of transactions and amount spent by a customer in the last 1 hour
w_1hr = Window.partitionBy("customer_id").orderBy(col("timestamp").cast("long")).rangeBetween(-3600, 0)

df_features = df_txn.withColumn("txn_count_1hr", count("txn_id").over(w_1hr)) \
                    .withColumn("amt_spent_1hr", sum("amount_inr").over(w_1hr))

# Calculate Z-Score for amount to detect anomalies
w_cust = Window.partitionBy("customer_id")
df_features = df_features.withColumn("avg_amt", avg("amount_inr").over(w_cust)) \
                         .withColumn("stddev_amt", expr("stddev(amount_inr) over (partition by customer_id) + 1")) \
                         .withColumn("amount_z_score", (col("amount_inr") - col("avg_amt")) / col("stddev_amt"))

# Join with customer dim
df_final = df_features.join(df_cust, on="customer_id", how="left")

# Save Processed Data
df_final.write.mode("overwrite").parquet("data/processed/model_ready_data.parquet")
spark.stop()