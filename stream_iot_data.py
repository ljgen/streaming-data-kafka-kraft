import json
import logging
import sys

from kafka import KafkaConsumer
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from datetime import datetime, timezone
from iot_data import generate_iot_data

# Kafka Configuration
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'iot_data'

# Cassandra Configuration
CASSANDRA_KEYSPACE = 'iot_data'
CASSANDRA_TABLE = 'sensor_data'
CASSANDRA_HOST = 'localhost'
CASSANDRA_PORT = "9042"

def create_keyspace(c_conn):
    keyspace_query = """
    CREATE KEYSPACE IF NOT EXISTS iot_data
    WITH REPLICATION = {
        'class': 'SimpleStrategy',
        'replication_factor': 1
        };
    """
    c_conn.execute(keyspace_query)

    print("Keyspace created successfully!")


def create_table(c_conn):
    table_query = """
    CREATE TABLE IF NOT EXISTS iot_data.sensor_data (
      device_id TEXT,
      timestamp TIMESTAMP,
      temperature DOUBLE,
      humidity DOUBLE,
      PRIMARY KEY (device_id, timestamp)
    );
    """
    c_conn.execute(table_query)

    print("Table created successfully!")


def insert_data(c_conn, messages):
    print("Starting to insert data...")

    for message  in messages:
        try:
            data =  message.value

            # Extract the required fields from the data
            device_id = data.get('device_id')
            unix_timestamp = data.get('timestamp')
            timestamp = datetime.fromtimestamp(unix_timestamp, timezone.utc)
            temperature = data.get('temperature')
            humidity = data.get('humidity')
    
            if not all([device_id, timestamp, temperature, humidity]):
                raise ValueError("Missing required fields in the data")

            insert_query = """
            INSERT INTO iot_data.sensor_data (
            device_id, timestamp, temperature, humidity)
            VALUES (%s, %s, %s, %s)
            """
            c_conn.execute(insert_query, (device_id, timestamp, temperature, humidity))

            # Log success
            logging.info(f"Data inserted for device_id: {device_id}, timestamp: {timestamp}, temperature: {temperature}, humidity: {humidity}")

        except ValueError as ve:
            logging.error(f"Data validation error: {ve} for message: {message}")
            continue  

        except Exception as e:
            logging.error(f'Could not insert data due to: {e} for message: {message}')
            continue


def cassandra_connection():
    conn = None

    try:
        # Connecting to the cassandra cluster
        auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
        cluster = Cluster([CASSANDRA_HOST], auth_provider=auth_provider)

        conn = cluster.connect()

        print("Cassandra connection created successfully!")

    except Exception as e:
        logging.error(f"Could not create cassandra connection: {e}")

    return conn


def consumer_connection():
    consumer = None

    try:
        consumer = KafkaConsumer(KAFKA_TOPIC,
                                 bootstrap_servers=KAFKA_BROKER,
                                 auto_offset_reset='earliest',
                                 enable_auto_commit=True,
                                 group_id="stream_iot_data",
                                 value_deserializer=lambda m: json.loads(m.decode('utf-8')))

        print("Kafka consumer connection created successfully!")

    except Exception as e:
        logging.error(f"Could not create consumer connection: {e}")

    return consumer


if __name__ == "__main__":
    # Establish Cassandra connection
    cs_conn = cassandra_connection()

    if cs_conn is not None:
        try:
            create_keyspace(cs_conn)
            create_table(cs_conn)
        
        except Exception as e:
            logging.error(f"Error creating Cassandra keyspace or table: {e}")
            sys.exit(1)

        kafka_consumer = consumer_connection()

        if kafka_consumer is not None:
            try:
                insert_data(cs_conn, kafka_consumer)
            
            except Exception as e:
                logging.error(f"Error inserting data into Cassandra: {e}")
                sys.exit(1)

        else:
            logging.error("Failed to connect to Kafka consumer.")
            sys.exit(1)        

    else:
        logging.error("Failed to connect to Cassandra.")
        sys.exit(1)           