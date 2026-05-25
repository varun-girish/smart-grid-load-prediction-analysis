from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.common.watermark_strategy import WatermarkStrategy

import json

# Create execution environment
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)

# Kafka source configuration
source = KafkaSource.builder() \
    .set_bootstrap_servers("localhost:9092") \
    .set_topics("weather-stream") \
    .set_group_id("flink-group") \
    .set_value_only_deserializer(SimpleStringSchema()) \
    .build()

# Create data stream
stream = env.from_source(
    source,
    WatermarkStrategy.no_watermarks(),
    "Kafka Source"
)

# Processing function
def process_weather(data):
    try:
        weather = json.loads(data)

        state = weather.get("state")
        temperature = weather.get("temperature")
        rainfall = weather.get("rainfall")

        # Load impact logic
        if temperature > 38:
            load_status = "High Cooling Load"
            estimated_change = "+300 MW"

        elif rainfall > 70:
            load_status = "Rain Impact Load"
            estimated_change = "-150 MW"

        else:
            load_status = "Normal Load"
            estimated_change = "0 MW"

        result = {
            "state": state,
            "temperature": temperature,
            "rainfall": rainfall,
            "load_status": load_status,
            "estimated_change": estimated_change
        }

        return json.dumps(result)

    except Exception as e:
        return f"Error: {str(e)}"

# Apply processing
processed_stream = stream.map(process_weather)

# Print output
processed_stream.print()

# Execute Flink job
env.execute("Real-Time Weather Load Analysis")