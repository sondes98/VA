FROM bitnami/spark:latest

USER root

# Fix the APT issue by ensuring the directory exists and updating package lists
RUN mkdir -p /var/lib/apt/lists/partial && \
    apt-get update && \
    apt-get install -y python3-pip

USER 1001

# Copy the application files into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Set the command to run the Spark application
CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1,org.elasticsearch:elasticsearch-spark-30_2.12:7.10.1", "spark_streaming.py"]
