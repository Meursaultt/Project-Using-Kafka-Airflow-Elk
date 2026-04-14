# Sensor Streaming Pipeline with Kafka, Airflow, and ELK

An end-to-end **streaming data engineering** project that simulates IoT sensor telemetry, publishes events to **Apache Kafka**, orchestrates producer/consumer jobs with **Apache Airflow**, and indexes/searches data in the **ELK stack** (Elasticsearch, Logstash, Kibana).

---

## Architecture

| Layer | Description |
|---|---|
| **Streaming** | Kafka cluster (Zookeeper, Broker, Schema Registry, Control Center) receives sensor events |
| **Orchestration** | Airflow DAGs schedule producer and consumer pipelines every 5 minutes |
| **Producer DAG** | Generates synthetic machine telemetry (`temperature`, `vibration`, `pressure`, `rpm`) and publishes to Kafka topic `sensor_data` |
| **Consumer DAG** | Consumes Kafka messages from `sensor_data` and indexes them into Elasticsearch |
| **Observability** | Kibana dashboards visualize indexed data and Logstash pipelines |
| **Containerization** | All services run with Docker Compose using shared external networks |

---

## Data Flow

1. `sensor_data_producer` DAG creates synthetic machine readings for 5 machines.
2. Events are published to Kafka topic `sensor_data`.
3. `sensor_data_consumer` DAG reads from Kafka with consumer group `sensor-group`.
4. Events are transformed into Elasticsearch documents.
5. Documents are indexed into Elasticsearch index `sensor_data`.
6. Kibana can be used to query and visualize indexed telemetry.

---

## Tech Stack

| Tool | Version | Role |
|---|---|---|
| Apache Airflow | 2.10.2 (Docker image base) | Workflow orchestration |
| Apache Kafka (Confluent Platform) | cp-server 6.2.2 | Event streaming |
| Zookeeper | Confluent image | Kafka coordination |
| Schema Registry | Confluent image | Schema services |
| Confluent Control Center | Confluent image | Kafka monitoring UI |
| Elasticsearch | 8.11.1 | Search/index engine |
| Logstash | 8.11.1 | Log parsing and ingestion |
| Kibana | 8.11.1 | Data visualization |
| PostgreSQL | 13 | Airflow metadata DB |
| Redis | 7.2 | Airflow Celery broker |
| Python | 3.11 | DAG logic and connectors |
| Docker Compose | - | Local infrastructure |

---

## Project Structure

```text
Project-Using-Kafka-Airflow-Elk/
├── Airflow/
│   ├── dags/
│   │   ├── sensor_airflow.py              # Producer DAG (Kafka publisher)
│   │   └── sensor_airflow_consumer.py     # Consumer DAG (Kafka -> Elasticsearch)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── docker-compose.yml
│   └── .env
├── Kafka/
│   └── docker-compose.yml
├── Elk/
│   ├── docker-compose.yml
│   ├── .env
│   ├── setup/
│   ├── elasticsearch/
│   ├── kibana/
│   └── logstash/
└── README.md
```

---




## Future Improvements

- Add data validation checks before indexing into Elasticsearch
- Add retry/DLQ strategy for failed Kafka messages
- Add Terraform/Kubernetes deployment manifests for production
- Add automated tests for DAG functions and integrations
- Add dashboards for anomaly detection on sensor telemetry

