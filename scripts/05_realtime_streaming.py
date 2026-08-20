import os
os.environ["PYSPARK_SUBMIT_ARGS"] = "--driver-memory 4g pyspark-shell"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, sum, count

# 1. Initialize Spark Session
spark = SparkSession.builder \
    .appName("Raksha_RealTime_Fraud_Detection") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

# Changing to v3 to completely bypass the old bad data!
stream_dir = "data/stream_input_v3"

# 2. Create the micro-batches from the EXACT Transactions file
if not os.path.exists(stream_dir):
    print("0. Preparing fresh micro-batches from Transactions...")
    # Explicitly point to the file we know contains amount_inr and txn_id
    df_static = spark.read.parquet("data/processed/model_ready_data.parquet").limit(20000)
    df_static.repartition(20).write.parquet(stream_dir)
    print("Success! 20 micro-batches ready.")

print("1. Auto-detecting schema from Parquet files...")
static_df = spark.read.parquet(stream_dir)
actual_schema = static_df.schema
static_df.printSchema()

# Dynamically find the correct time column
time_col = "txn_timestamp" if "txn_timestamp" in static_df.columns else "timestamp"
print(f"2. Found time column: '{time_col}'. Starting Real-Time Stream...")

# 3. Stream using the automatically detected schema
raw_stream = spark.readStream \
    .format("parquet") \
    .schema(actual_schema) \
    .option("maxFilesPerTrigger", 1) \
    .load(stream_dir)

# 4. REAL-TIME FEATURE ENGINEERING (Live Leaderboard)
velocity_features = raw_stream \
    .groupBy(
        window(col(time_col).cast("timestamp"), "1 hour", "1 minute"), 
        col("customer_id")
    ) \
    .agg(
        count("txn_id").alias("txn_count_1hr"),
        sum("amount_inr").alias("amt_spent_1hr")
    ) \
    .orderBy(col("txn_count_1hr").desc()) # Push highest frequency customers to the top

# 5. Push to Sink
query = velocity_features.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .trigger(processingTime="2 seconds") \
    .start()

query.awaitTermination()