import json
import time
import random
from kafka import KafkaProducer

STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
    "Chhattisgarh", "Delhi", "Goa", "Gujarat",
    "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh",
    "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha",
    "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal"
]

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("🌦 Weather Producer Started...")

while True:
    state = random.choice(STATES)

    temperature = random.randint(18, 45)
    rainfall = random.randint(0, 100)

    data = {
        "state": state,
        "temperature": temperature,
        "rainfall": rainfall
    }

    producer.send("weather-stream", value=data)
    producer.flush()

    print("Sent:", data)
    time.sleep(3)