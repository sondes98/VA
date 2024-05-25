from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType

# Define the schema for the laptop data
schema = StructType([
    StructField("Product", StringType(), True),
    StructField("Company", StringType(), True),
    StructField("Price", StringType(), True),
    # Add other fields as necessary
])

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaSparkElasticsearch") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoints") \
    .config("spark.es.nodes", "elasticsearch") \
    .config("spark.es.port", "9200") \
    .getOrCreate()

# Read from Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "laptops") \
    .load()

# Convert the value column from bytes to string
df = df.selectExpr("CAST(value AS STRING)")

# Parse the JSON string
parsed_df = df.select(from_json(col("value"), schema).alias("data"))

# Select the individual fields from the parsed data
parsed_df = parsed_df.select("data.*")

# Print the schema of the parsed DataFrame
parsed_df.printSchema()

# Write the parsed DataFrame to Elasticsearch
query = parsed_df \
    .writeStream \
    .outputMode("append") \
    .format("org.elasticsearch.spark.sql") \
    .option("checkpointLocation", "/tmp/checkpoints") \
    .start("laptops_index/laptops")

# Wait for the stream to finish
query.awaitTermination()
