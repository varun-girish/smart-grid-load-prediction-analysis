from flask import Flask, jsonify
from kafka import KafkaConsumer
import json
import threading

app = Flask(__name__)

latest_weather = {}

def consume_weather():
    global latest_weather

    consumer = KafkaConsumer(
        "weather-stream",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="latest",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    for message in consumer:
        data = message.value

        temp = data["temperature"]
        rain = data["rainfall"]

        if temp > 38:
            impact = "High Cooling Load"
            load_mw = 300
        elif rain > 70:
            impact = "Low Demand (Rain Impact)"
            load_mw = -150
        else:
            impact = "Normal Load"
            load_mw = 0

        data["load_impact"] = impact
        data["estimated_load_change_MW"] = load_mw

        latest_weather = data

thread = threading.Thread(target=consume_weather)
thread.daemon = True
thread.start()

@app.route("/latest_weather", methods=["GET"])
def get_weather():
    return jsonify(latest_weather)

if __name__ == "__main__":
    app.run(port=5003)