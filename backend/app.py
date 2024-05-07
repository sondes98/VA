from flask import Flask, jsonify, request
import pyttsx3
import pandas as pd
import speech_recognition as sr
import os

app = Flask(__name__)

# Initialize speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Function to read laptop data from CSV file
def read_laptop_data(file_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, file_name)
    laptops_df = pd.read_csv(file_path, delimiter=',')
    laptops_df.columns = laptops_df.columns.str.strip()
    return laptops_df

# Function to filter laptops based on criteria
# Function to filter laptops based on criteria
def filter_laptops(laptops_df, criteria):
    filtered_laptops_df = laptops_df.copy()
    valid_keys = laptops_df.columns.tolist()

    for key, value in criteria.items():
        if key not in valid_keys:
            return {"error": f"'{key}' is not a valid key in the laptop data. Valid keys are: {valid_keys}"}

    if 'Company' in criteria and 'Company' in filtered_laptops_df.columns:
        filtered_laptops_df = filtered_laptops_df[filtered_laptops_df['Company'].str.lower() == criteria['Company'].lower()]
    else:
        return {"error": "'Company' column does not exist in the laptop data or brand criteria not specified."}

    if 'Price' in criteria and 'Price' in filtered_laptops_df.columns:
        try:
            # Remove commas from price input and convert to float
            criteria['Price'] = float(criteria['Price'].replace(',', ''))
        except ValueError:
            return {"error": "Invalid price format. Price must be a number."}
        filtered_laptops_df = filtered_laptops_df[filtered_laptops_df['Price'] <= criteria['Price']]
    else:
        return {"error": "'Price' column does not exist in the laptop data or price criteria not specified."}
    
    return filtered_laptops_df.to_dict(orient='records')

# Function to recognize speech
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        return query
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None

# Function to speak response
def speak_response(response):
    engine.say(response)

# Route for main interaction
@app.route('/assistant', methods=['POST'])
def main():
    if not request.json:
        return jsonify({"error": "Request body is missing"}), 400
    
    # Read laptop data
    laptops_df = read_laptop_data('Laptop_data.csv')

    # Get user input
    data = request.json
    brand = data.get('brand')
    price = data.get('price')

    if not brand or not price:
        return jsonify({"error": "Brand or price is missing"}), 400

    criteria = {'Company': brand, 'Price': price}

    # Filter laptops
    filtered_laptops = filter_laptops(laptops_df, criteria)

    if isinstance(filtered_laptops, list):
        # Construct a string representation of each laptop
        laptop_details = []
        for laptop in filtered_laptops:
            details = f"{laptop['Product']} - {laptop['Price']} euros"
            laptop_details.append(details)
        laptop_details_str = ". ".join(laptop_details)
        
        # Speak out the list of laptops
        speak_response(f"Here are some laptops that match your criteria: {laptop_details_str}")
    else:
        speak_response("Sorry, no laptops matching your criteria were found.")

    return jsonify({"laptops": filtered_laptops}), 200
if __name__ == '__main__':
    app.run(debug=True)
