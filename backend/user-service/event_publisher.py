"""
Event Publisher - Publishes domain events to RabbitMQ and stores them in event store.
Follows Event Sourcing pattern for audit trail and event-driven architecture.
"""
import json
import pika
import os
from datetime import datetime
from models import Event
from flask import current_app


class EventPublisher:
    """
    Publishes domain events to RabbitMQ message broker and event store.
    """

    def __init__(self, db_session):
        """
        Initialize event publisher with database session.

        Args:
            db_session: SQLAlchemy database session for event store
        """
        self.db_session = db_session
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'talentlink')
        self.rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'talentlink123')

    def _get_rabbitmq_connection(self):
        """
        Create RabbitMQ connection.

        Returns:
            pika.BlockingConnection: RabbitMQ connection
        """
        credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
        parameters = pika.ConnectionParameters(
            host=self.rabbitmq_host,
            port=self.rabbitmq_port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        return pika.BlockingConnection(parameters)

    def publish_event(self, event_type, aggregate_id, aggregate_type, event_data, user_id=None):
        """
        Publish a domain event to both event store (database) and RabbitMQ.

        This follows the Event Sourcing pattern:
        1. Store event in event store for audit trail and replay capability
        2. Publish event to message broker for asynchronous processing

        Args:
            event_type (str): Type of event (e.g., "UserDeleted")
            aggregate_id (str): ID of the aggregate root (e.g., user_id)
            aggregate_type (str): Type of aggregate (e.g., "UserProfile")
            event_data (dict): Event payload data
            user_id (str, optional): ID of user who triggered the event

        Returns:
            Event: The stored event object
        """
        try:
            # 1. Store event in event store (database)
            event = Event(
                event_type=event_type,
                aggregate_id=str(aggregate_id),
                aggregate_type=aggregate_type,
                event_data=event_data,
                user_id=user_id,
                version=1
            )
            self.db_session.add(event)
            self.db_session.commit()

            current_app.logger.info(
                f"✅ Event stored in event store: {event_type} (ID: {event.event_id}, "
                f"Aggregate: {aggregate_type}#{aggregate_id})"
            )

            # 2. Publish event to RabbitMQ
            self._publish_to_rabbitmq(event_type, event.to_dict())

            return event

        except Exception as e:
            current_app.logger.error(f"❌ Failed to publish event {event_type}: {e}")
            self.db_session.rollback()
            raise

    def _publish_to_rabbitmq(self, event_type, event_dict):
        """
        Publish event to RabbitMQ exchange.

        Uses topic exchange for flexible routing:
        - Exchange: "talentlink.events"
        - Routing key: event type (e.g., "user.deleted")

        Args:
            event_type (str): Type of event for routing key
            event_dict (dict): Complete event data to publish
        """
        connection = None
        try:
            # Connect to RabbitMQ
            connection = self._get_rabbitmq_connection()
            channel = connection.channel()

            # Declare topic exchange (idempotent - safe to call multiple times)
            exchange_name = 'talentlink.events'
            channel.exchange_declare(
                exchange=exchange_name,
                exchange_type='topic',
                durable=True
            )

            # Convert event type to routing key (e.g., "UserDeleted" -> "user.deleted")
            routing_key = self._event_type_to_routing_key(event_type)

            # Publish message
            message = json.dumps(event_dict)
            channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json',
                    timestamp=int(datetime.utcnow().timestamp())
                )
            )

            current_app.logger.info(
                f"✅ Event published to RabbitMQ: {routing_key} "
                f"(Exchange: {exchange_name}, Event ID: {event_dict.get('event_id')})"
            )

        except Exception as e:
            current_app.logger.error(f"❌ Failed to publish to RabbitMQ: {e}")
            # Don't raise - event is already stored in event store
            # A separate process could retry publishing from event store

        finally:
            if connection and not connection.is_closed:
                connection.close()

    def _event_type_to_routing_key(self, event_type):
        """
        Convert event type to routing key.

        Examples:
            "UserDeleted" -> "user.deleted"
            "UserUpdated" -> "user.updated"
            "ProfileCreated" -> "profile.created"

        Args:
            event_type (str): CamelCase event type

        Returns:
            str: Routing key in dot notation
        """
        # Convert CamelCase to snake_case with dots
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1.\2', event_type)
        routing_key = re.sub('([a-z0-9])([A-Z])', r'\1.\2', s1).lower()
        return routing_key
