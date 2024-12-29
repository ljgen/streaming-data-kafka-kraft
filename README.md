# **Streaming Data with Kafka: Exploring KRaft (Kafka Raft)**

# Overview
This project demonstrates a data engineering pipeline that simulates IoT sensor data, streams it using Apache Kafka (Kafka Kraft mode), and ingests the data into a Cassandra database. The pipeline mimics real-time data processing and storage scenarios, suitable for Smart City or Smart Home use cases.

# Pipeline Architecture
### 1. Data Simulation:
- Python script (`iot_data.py`) generates simulated IoT data in real-time.
- Data includes fields like `device_id`, `timestamp`, `temperature` and `humidity`.
### 2. Data Streaming:
- The generated data is streamed to a Kafka topic using a Kafka producer.
- Kafka operates in Kraft mode, eliminating the need for ZooKeeper.
### 3. Data Consumption:
- A Kafka consumer script (`stream_iot_data.py`) reads the data from the Kafka topic.
- The consumer processes the incoming data and inserts it into a Cassandra database for storage and querying.

# Technologies Used
- Python: For data simulation, Kafka producer, and consumer.
- Apache Kafka: For real-time data streaming in Kraft mode.
- Apache Cassandra: For scalable and fault-tolerant data storage.
- Docker Compose: To orchestrate Kafka and Cassandra services.
- Linux: Host environment for running Docker containers.

# Setup Instructions
## Prerequisites
- Docker and Docker Compose installed.
- Python 3.8+ with the required libraries (`kafka-python`, `cassandra-driver`).
- Sufficient system resources to run Kafka and Cassandra containers.
## Pipeline Components
### 1. Kafka Setup:
- Kafka runs in `Kraft mode` as a single-node broker via Docker Compose.
- Kafka topic: `iot_data`.
### 2. Cassandra Setup:
- Cassandra is set up using Docker Compose.
- Keyspace: `iot_data`.
- Table: `sensor_data`.
### 3. Scripts:
- `iot_data.py`: Simulates and sends IoT data to Kafka.
- `stream_iot_data.py`: Consumes Kafka messages and inserts them into Cassandra.

## How It Works
### 1. Start Services:
- Run `docker-compose up` to start Kafka and Cassandra containers.
### 2. Generate IoT Data:
- Execute `iot_data.py` to simulate and produce sensor data to Kafka.
### 3. Stream and Ingest Data:
- Run `stream_iot_data.py` to consume Kafka messages and store them in Cassandra.

## Sample Output
### Kafka Producer Output:
```
{
    'device_id': 'device_2', 
    'timestamp': 1735444918.3166866, 
    'temperature': 26.51, 
    'humidity': 40.78
}
```
### Cassandra Insert:
```
INSERT INTO iot_data.sensor_data (
device_id, timestamp, temperature, humidity)
VALUES ('device_2', 2024-12-29 04:01:58.316000+0000, 26.51, 40.78)
```

## Directory Structure
```
├── data/                     # Directory for storing test data or logs
├── docker-compose.yml        # Docker Compose file for Kafka and Cassandra setup
├── iot_data.py               # IoT data simulation and Kafka producer script
├── stream_iot_data.py        # Kafka consumer and Cassandra insertion script
└── README.md                 # Project documentation
```
