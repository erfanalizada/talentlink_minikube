"""
RabbitMQ event consumer for auth service.
Subscribes to UserDeleted events and deletes users from Keycloak.
"""
import json
import pika
import os
import time
from keycloak import KeycloakAdmin


class EventConsumer:
    """
    Consumes UserDeleted events from RabbitMQ and deletes users from Keycloak.
    """

    def __init__(self, keycloak_admin):
        """
        Initialize event consumer with RabbitMQ connection details.

        Args:
            keycloak_admin: KeycloakAdmin instance for user management
        """
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'talentlink')
        self.rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'talentlink123')

        self.admin = keycloak_admin
        self.connection = None
        self.channel = None

    def connect(self):
        """
        Connect to RabbitMQ with retry logic.
        """
        max_retries = 10
        retry_delay = 5  # seconds

        for attempt in range(max_retries):
            try:
                print(f"🔌 Connecting to RabbitMQ at {self.rabbitmq_host}:{self.rabbitmq_port} (attempt {attempt + 1}/{max_retries})...")

                credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
                parameters = pika.ConnectionParameters(
                    host=self.rabbitmq_host,
                    port=self.rabbitmq_port,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()

                print(f"✅ Connected to RabbitMQ successfully!")
                return True

            except Exception as e:
                print(f"❌ Failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("❌ Max retries reached. Could not connect to RabbitMQ.")
                    return False

    def setup_queue(self):
        """
        Set up exchange, queue, and bindings for consuming UserDeleted events.
        """
        try:
            # Declare exchange (same as publisher)
            exchange_name = 'talentlink.events'
            self.channel.exchange_declare(
                exchange=exchange_name,
                exchange_type='topic',
                durable=True
            )

            # Declare queue for auth service
            queue_name = 'auth.user.deleted'
            self.channel.queue_declare(
                queue=queue_name,
                durable=True
            )

            # Bind queue to exchange with routing key pattern
            # Listen for user.deleted events
            routing_key = 'user.deleted'
            self.channel.queue_bind(
                exchange=exchange_name,
                queue=queue_name,
                routing_key=routing_key
            )

            print(f"✅ Queue setup complete:")
            print(f"   Exchange: {exchange_name}")
            print(f"   Queue: {queue_name}")
            print(f"   Routing Key: {routing_key}")

            return queue_name

        except Exception as e:
            print(f"❌ Failed to setup queue: {e}")
            raise

    def start_consuming(self):
        """
        Start consuming events from RabbitMQ.
        This is a blocking call that runs until interrupted.
        """
        try:
            if not self.connect():
                print("❌ Cannot start consuming: RabbitMQ connection failed")
                return

            queue_name = self.setup_queue()

            # Set QoS (quality of service) - process one message at a time
            self.channel.basic_qos(prefetch_count=1)

            # Start consuming
            print(f"👂 Starting to consume events from queue: {queue_name}")
            print("Waiting for UserDeleted events...")

            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self.on_message,
                auto_ack=False  # Manual acknowledgment
            )

            self.channel.start_consuming()

        except KeyboardInterrupt:
            print("\n⏹️  Stopping event consumer...")
            self.stop()
        except Exception as e:
            print(f"❌ Error in event consumer: {e}")
            import traceback
            traceback.print_exc()
            self.stop()

    def on_message(self, channel, method, properties, body):
        """
        Callback function when a message is received.

        Args:
            channel: Pika channel
            method: Delivery method
            properties: Message properties
            body: Message body (bytes)
        """
        try:
            # Decode message
            message = json.loads(body.decode('utf-8'))

            print(f"\n📩 Received event: {method.routing_key}")
            print(f"   Event ID: {message.get('event_id')}")
            print(f"   Event Type: {message.get('event_type')}")
            print(f"   Aggregate: {message.get('aggregate_type')}#{message.get('aggregate_id')}")

            # Process UserDeleted event
            if message.get('event_type') == 'UserDeleted':
                self.process_user_deleted(message)

            # Acknowledge message
            channel.basic_ack(delivery_tag=method.delivery_tag)
            print("✅ Message processed and acknowledged")

        except Exception as e:
            print(f"❌ Error processing message: {e}")
            import traceback
            traceback.print_exc()

            # Reject message and don't requeue (send to dead letter queue if configured)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def process_user_deleted(self, event):
        """
        Process UserDeleted event by deleting user from Keycloak.

        Args:
            event (dict): Event data containing user details
        """
        try:
            event_data = event.get('event_data', {})

            user_id = event_data.get('user_id')
            username = event_data.get('username')
            email = event_data.get('email')

            print(f"\n🗑️  Processing UserDeleted event:")
            print(f"   User ID: {user_id}")
            print(f"   Username: {username}")
            print(f"   Email: {email}")

            if not user_id:
                print("⚠️ No user_id found in event data. Skipping deletion from Keycloak.")
                return

            # Delete user from Keycloak
            try:
                print(f"🔄 Deleting user from Keycloak: {user_id}")
                self.admin.delete_user(user_id=user_id)
                print(f"✅ User '{username}' (ID: {user_id}) deleted from Keycloak successfully!")

            except Exception as kc_error:
                error_str = str(kc_error)
                # Check if user was not found (already deleted or never existed)
                if "404" in error_str or "Not found" in error_str or "Could not find user" in error_str:
                    print(f"⚠️ User not found in Keycloak (ID: {user_id}). May have been already deleted.")
                else:
                    print(f"❌ Failed to delete user from Keycloak: {kc_error}")
                    raise

        except Exception as e:
            print(f"❌ Error in process_user_deleted: {e}")
            import traceback
            traceback.print_exc()

    def stop(self):
        """Stop consuming and close connection."""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.stop_consuming()
                print("⏹️  Stopped consuming")

            if self.connection and not self.connection.is_closed:
                self.connection.close()
                print("🔌 Closed RabbitMQ connection")

        except Exception as e:
            print(f"⚠️ Error closing connection: {e}")
