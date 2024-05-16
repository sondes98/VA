from flask import Flask, request, jsonify
from confluent_kafka import Producer

app = Flask(__name__)

conf = {'bootstrap.servers': "localhost:9092"}
producer = Producer(**conf)

@app.route('/add-to-bag', methods=['POST'])
def add_to_bag():
    laptop = request.json
    try:
        producer.produce('laptops', key=str(laptop['Product']), value=str(laptop))
        producer.flush()
        return jsonify({'message': 'Laptop added to bag and sent to Kafka'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to send laptop to Kafka', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
