FROM bitnami/spark:latest

COPY . /app
WORKDIR /app

CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1,org.elasticsearch:elasticsearch-spark-30_2.12:7.10.2", "spark_streaming.py"]
