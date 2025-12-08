"""
RabbitMQ event consumer for notification service.
Subscribes to ApplicationAccepted events and sends email notifications.
"""
import json
import pika
import os
import time
import requests
from email_sender import EmailSender


class EventConsumer:
    """
    Consumes events from RabbitMQ and processes them.
    """

    def __init__(self):
        """Initialize event consumer with RabbitMQ connection details."""
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'talentlink')
        self.rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'talentlink123')
        self.job_service_url = os.getenv('JOB_SERVICE_URL', 'http://job-service:5000')

        self.email_sender = EmailSender()
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
        Set up exchange, queue, and bindings for consuming events.
        """
        try:
            # Declare exchange (same as publisher)
            exchange_name = 'talentlink.events'
            self.channel.exchange_declare(
                exchange=exchange_name,
                exchange_type='topic',
                durable=True
            )

            # Declare queue for notification service
            queue_name = 'notification.application.accepted'
            self.channel.queue_declare(
                queue=queue_name,
                durable=True
            )

            # Bind queue to exchange with routing key pattern
            # Listen for application.accepted events
            routing_key = 'application.accepted'
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
            print("Waiting for ApplicationAccepted events...")

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

            # Process ApplicationAccepted event
            if message.get('event_type') == 'ApplicationAccepted':
                self.process_application_accepted(message)

            # Acknowledge message
            channel.basic_ack(delivery_tag=method.delivery_tag)
            print("✅ Message processed and acknowledged")

        except Exception as e:
            print(f"❌ Error processing message: {e}")
            import traceback
            traceback.print_exc()

            # Reject message and don't requeue (send to dead letter queue if configured)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def process_application_accepted(self, event):
        """
        Process ApplicationAccepted event by sending email notification.

        Args:
            event (dict): Event data containing application details
        """
        try:
            event_data = event.get('event_data', {})

            application_id = event_data.get('application_id')
            job_id = event_data.get('job_id')
            employee_email = event_data.get('employee_email')
            employee_username = event_data.get('employee_username')

            print(f"\n📧 Processing ApplicationAccepted event:")
            print(f"   Application ID: {application_id}")
            print(f"   Job ID: {job_id}")
            print(f"   Employee: {employee_username} ({employee_email})")

            if not employee_email:
                print("⚠️ No employee email found in event data. Skipping email.")
                return

            # Fetch job details to get job title
            job_title = self._fetch_job_title(job_id)

            # Send email notification
            success = self.email_sender.send_application_accepted_email(
                employee_email=employee_email,
                employee_username=employee_username or "Candidate",
                job_title=job_title
            )

            if success:
                print(f"✅ Email notification sent successfully to {employee_email}")
            else:
                print(f"❌ Failed to send email notification to {employee_email}")

        except Exception as e:
            print(f"❌ Error in process_application_accepted: {e}")
            import traceback
            traceback.print_exc()

    def _fetch_job_title(self, job_id):
        """
        Fetch job title from job-service.

        Args:
            job_id (int): Job ID

        Returns:
            str: Job title or None
        """
        try:
            response = requests.get(
                f"{self.job_service_url}/api/jobs/{job_id}",
                timeout=5
            )
            if response.status_code == 200:
                job_data = response.json()
                return job_data.get('title')
        except Exception as e:
            print(f"⚠️ Could not fetch job title for job {job_id}: {e}")

        return None

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
