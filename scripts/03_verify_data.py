import os
os.environ['HADOOP_HOME'] = 'C:\\hadoop'

from pyspark.sql import SparkSession

# 1. Initialize Spark
spark = SparkSession.builder.appName("VerifyData").getOrCreate()

# 2. Load the processed data
df = spark.read.parquet("data/processed/model_ready_data.parquet")

# 3. Inspect the results
print(f"Total rows: {df.count()}")
df.printSchema()
df.show(5, truncate=False)