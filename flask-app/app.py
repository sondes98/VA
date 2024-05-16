from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import logging
from confluent_kafka import Producer

app = Flask(__name__)
CORS(app, resources={r"/assistant": {"origins": "http://localhost:3000"}})

# Kafka Producer configuration
conf = {'bootstrap.servers': "localhost:9092"}
producer = Producer(**conf)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Function to read laptop data from CSV file
def read_laptop_data(file_name):
    try:
        laptops_df = pd.read_csv(file_name, delimiter=',')
        laptops_df.columns = laptops_df.columns.str.strip()
        return laptops_df
    except Exception as e:
        logging.error(f"Error reading laptop data: {e}")
        raise

# Function to filter laptops based on criteria
def filter_laptops(laptops_df, criteria):
    try:
        # Ensure the laptop data DataFrame is not empty
        if laptops_df.empty:
            return {"error": "Laptop data is empty. Unable to filter."}

        # Copy the original DataFrame to avoid modifying the original data
        filtered_laptops_df = laptops_df.copy()

        # Check if the DataFrame contains necessary columns
        required_columns = ['Company', 'Price']
        missing_columns = [col for col in required_columns if col not in filtered_laptops_df.columns]
        if (missing_columns):
            return {"error": f"Missing columns in laptop data: {', '.join(missing_columns)}"}

        # Check for invalid keys in the criteria
        valid_keys = filtered_laptops_df.columns.tolist()
        for key in criteria.keys():
            if key not in valid_keys:
                return {"error": f"'{key}' is not a valid key in the laptop data. Valid keys are: {', '.join(valid_keys)}"}

        # Filter by brand
        if 'Company' in criteria:
            brand = criteria['Company'].strip().lower()  # Normalize brand name
            logging.info(f"Filtering laptops by brand: {brand}")
            filtered_laptops_df = filtered_laptops_df[filtered_laptops_df['Company'].str.strip().str.lower() == brand]

        # Filter by price
        if 'Price' in criteria:
            try:
                price = float(criteria['Price'].replace(',', ''))  # Remove commas and convert to float
                logging.info(f"Filtering laptops by price: <= {price}")
                filtered_laptops_df = filtered_laptops_df[filtered_laptops_df['Price'] <= price]
            except ValueError:
                return {"error": "Invalid price format. Price must be a number."}

        # Convert the filtered DataFrame to a list of dictionaries
        filtered_laptops = filtered_laptops_df.to_dict(orient='records')
        logging.info(f"Filtered laptops: {filtered_laptops}")

        return filtered_laptops

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

# Route for main interaction
@app.route('/assistant', methods=['POST'])
def main():
    try:
        if not request.json:
            logging.error("Request body is missing")
            return jsonify({"error": "Request body is missing"}), 400

        # Read laptop data
        laptops_df = read_laptop_data('Laptop_data.csv')

        # Get user input
        data = request.json
        brand = data.get('brand')
        price = data.get('price')

        if not brand or not price:
            logging.error("Brand or price is missing")
            return jsonify({"error": "Brand or price is missing"}), 400

        criteria = {'Company': brand, 'Price': price}

        # Filter laptops
        filtered_laptops = filter_laptops(laptops_df, criteria)

        if isinstance(filtered_laptops, list):
            if filtered_laptops:
                return jsonify({"laptops": filtered_laptops}), 200
            else:
                logging.info("No laptops matching the criteria were found")
                return jsonify({"error": "Sorry, no laptops matching your criteria were found."}), 404
        else:
            return jsonify(filtered_laptops), 400
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

# Route to add laptop to bag and send to Kafka
@app.route('/add-to-bag', methods=['POST'])
def add_to_bag():
    laptop = request.json
    try:
        producer.produce('laptops', key=str(laptop['Product']), value=str(laptop))
        producer.flush()
        return jsonify({'message': 'Laptop added to bag and sent to Kafka'}), 200
    except Exception as e:
        logging.error(f"Failed to send laptop to Kafka: {e}")
        return jsonify({'error': 'Failed to send laptop to Kafka', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
