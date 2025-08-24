import asyncio
import logging

from app.queue.consumer import QueueConsumer


logger = logging.getLogger(__name__)


async def main() -> None:
    consumer = QueueConsumer()
    logger.info("Worker runner started")
    while True:
        await consumer.run_once()


if __name__ == "__main__":
    asyncio.run(main())



