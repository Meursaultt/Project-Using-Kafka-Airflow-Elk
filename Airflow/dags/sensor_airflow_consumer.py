import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
import json
from datetime import datetime
import logging

from kafka import KafkaConsumer
from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)

def index_to_elasticsearch(es, sensor_data):
    try:
        # Producer sends ISO format (e.g. 2026-03-13T12:34:56.123456)
        timestamp_str = sensor_data['timestamp']
        if 'T' in timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        iso_timestamp = timestamp.isoformat() if timestamp.tzinfo else timestamp.isoformat() + 'Z'

        # Index the data into Elasticsearch
        document = {
            'machine_id': sensor_data['machine_id'],
            'temperature': sensor_data['temperature'],
            'vibration': sensor_data['vibration'],
            'pressure': sensor_data['pressure'],
            'rpm': sensor_data['rpm'],
            'timestamp': iso_timestamp
        }
        # Compatible with Elasticsearch Python clients that use either
        # "document" (newer) or "body" (older) in es.index().
        try:
            es.index(index='sensor_data', document=document)
        except TypeError:
            es.index(index='sensor_data', body=document)
    except Exception as e:
        logger.exception("Failed to index data: %s", e)


def consume_data():
    # Initialize the Elasticsearch client
    es = Elasticsearch(['http://elasticsearch:9200'])

    # Create a Kafka consumer (broker:9092 when running in Airflow Docker)
    consumer = KafkaConsumer(
        'sensor_data',
        bootstrap_servers='broker:9092',
        auto_offset_reset='earliest',
        group_id='sensor-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=3000
    )

    max_messages_per_run = 50
    processed = 0

    try:
        for message in consumer:
            sensor_data = message.value

            # Index data into Elasticsearch.
            index_to_elasticsearch(es, sensor_data)
            processed += 1
            logger.info("Indexed to Elasticsearch: %s", sensor_data)

            if processed >= max_messages_per_run:
                logger.info("Reached max messages for this run: %s", max_messages_per_run)
                break
    finally:
        consumer.close()
        logger.info("Kafka consumer closed. Processed %s messages.", processed)
    
dag = DAG(
    dag_id = "sensor_data_consumer",
    default_args = {
        "owner" : "Anas EL Meslouti",
        "start_date" : airflow.utils.dates.days_ago(1),
    },
    schedule_interval = "*/5 * * * *",
    catchup = False
)

start = PythonOperator(
    task_id = "start",
    python_callable = lambda: print("Jobs Started"),
    dag=dag
)

python_job = PythonOperator(
    task_id="sensor_data_consumer",
    python_callable=consume_data,
    dag=dag
)

end = PythonOperator(
    task_id="end",
    python_callable = lambda: print("Jobs completed successfully"),
    dag=dag
)

start >> python_job >> end