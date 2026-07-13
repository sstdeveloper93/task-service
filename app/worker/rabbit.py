import aio_pika
import json
from uuid import UUID
from app.core.config import settings

QUEUE_NAME = "tasks_queue"

class RabbitMQPublisher:
    def __init__(self, channel: aio_pika.abc.AbstractChannel):
        self.channel = channel
        self.queue = None

    async def declare_queue(self):

        self.queue = await self.channel.declare_queue(
            QUEUE_NAME, 
            durable=True, 
            arguments={"x-max-priority": 10}
        )

    async def publish_task(self, task_id: UUID, priority: int):
        message = aio_pika.Message(
            body=json.dumps({"task_id": str(task_id)}).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            priority=priority
        )
        await self.channel.default_exchange.publish(message, routing_key=QUEUE_NAME)


publisher_instance: RabbitMQPublisher | None = None

async def init_rabbitmq():
    global publisher_instance
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    publisher_instance = RabbitMQPublisher(channel)
    await publisher_instance.declare_queue()

async def close_rabbitmq():
    if publisher_instance and publisher_instance.channel.connection:
        await publisher_instance.channel.connection.close()

def get_rabbit_publisher() -> RabbitMQPublisher:
    return publisher_instance
