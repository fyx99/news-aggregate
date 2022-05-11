
import threading
from db.config import RABBIT_CONNECTION_DETAILS
import pika
import json

from logger import get_logger
logger = get_logger()

EXCHANGE_NAME = "JOBS"
ROUTING_KEYS = ["RSS", "HTML", "FEATURE"]

class MessageBroker:
    #connection = None
    connections = {}
    channels = {}
    
    def __init__(self):
        self.connect()


    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        """Close Postgres Connection
        """
        #if self.connection is not None:
        self.disconnect()

    def disconnect(self):
        for connection in self.connections.values():
            connection.close()

    def connect(self):
        """Connect to Rabbit MQ
        """
        credentials = pika.PlainCredentials(RABBIT_CONNECTION_DETAILS["user"], RABBIT_CONNECTION_DETAILS["password"])
        parameters = pika.ConnectionParameters(RABBIT_CONNECTION_DETAILS["host"], RABBIT_CONNECTION_DETAILS["port"], '/', credentials, heartbeat=1200)
        new_connection = pika.BlockingConnection(parameters)
        self.connections[threading.get_ident()] = new_connection
        new_channel = new_connection.channel()
        self.channels[threading.get_ident()] = new_channel
        new_channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
        for route in ROUTING_KEYS:
            new_channel.queue_declare(route, durable=True)      #, arguments={"x-queue-mode": "lazy"}
            new_channel.queue_bind(exchange=EXCHANGE_NAME, queue=route, routing_key=route)
        logger.debug(f"RABBIT CONNECTION UP")
        return new_channel
        
    # def add_channel(self):
    #     new_channel = self.connection.channel()
    #     self.channels[threading.get_ident()] = new_channel
    #     new_channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
    #     for route in ROUTING_KEYS:
    #         new_channel.queue_declare(route, durable=True)
    #         new_channel.queue_bind(exchange=EXCHANGE_NAME, queue=route, routing_key=route)
    #     return new_channel

    def get_channel(self):
        return self.channels[threading.get_ident()] if threading.get_ident() in self.channels else self.connect()

    def put_task(self, route, body):
        # timeout 30 min
        self.get_channel().basic_publish(exchange=EXCHANGE_NAME, routing_key=route, body=json.dumps(body), properties=pika.BasicProperties(delivery_mode=2, expiration='1800000'))

    def get_task(self, route):
        method_frame, header_frame, body = self.get_channel().basic_get(route, auto_ack=True)
        if method_frame is None:
            return False
        return json.loads(body.decode())

    
    def get_task_batch(self, route, n):
        results = []
        for _ in range(n):
            method_frame, header_frame, body = self.get_channel().basic_get(route, auto_ack=True)
            if method_frame is None:
                break
            results.append(json.loads(body.decode()))
        return results




if __name__ == "__main__":
    with MessageBroker() as rb:
        rb.put_task("RSS", {"a": 1})
        # rb.put_task("RSS", "asdas")
        import time
        time.sleep(.8)
        rb.get_task("RSS")

        

