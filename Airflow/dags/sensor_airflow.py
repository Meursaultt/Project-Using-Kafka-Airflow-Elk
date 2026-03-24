from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

import json
import random
import logging
from datetime import datetime
from kafka import KafkaProducer

logger = logging.getLogger(__name__)

KAFKA_TOPIC = "sensor_data"
KAFKA_BOOTSTRAP_SERVERS = "broker:9092"

def generate_machine_data(machine_id: int) -> dict:
    
    temperature = random.uniform(60, 90)
    vibration = random.uniform(0.2, 1.5)
    pressure = random.uniform(100, 300)
    rpm = random.randint(1000, 5000)

    return {
        "machine_id": machine_id,
        "temperature": round(temperature, 2),
        "vibration": round(vibration, 2),
        "pressure": round(pressure, 2),
        "rpm": rpm,
        "timestamp": datetime.utcnow().isoformat()
    }


def stream_data():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5
    )

    try:
        for sensor_id in range(1, 6):  
            data = generate_machine_data(sensor_id)
            producer.send(KAFKA_TOPIC, value=data)
            logger.info(f"Sent data: {data}")

        producer.flush()

    except Exception as e:
        logger.error(f"Kafka producer error: {e}")
        raise

    finally:
        producer.close()


with DAG(
    dag_id="sensor_data_producer",
    start_date=days_ago(1),
    schedule="*/5 * * * *",
    catchup=False,
    tags=["kafka", "iot", "streaming"]
) as dag:

    start = PythonOperator(
        task_id="start",
        python_callable=lambda: logger.info("Job started")
    )

    produce_sensor_data = PythonOperator(
        task_id="produce_sensor_data",
        python_callable=stream_data
    )

    end = PythonOperator(
        task_id="end",
        python_callable=lambda: logger.info("Job finished successfully")
    )

    start >> produce_sensor_data >> end
