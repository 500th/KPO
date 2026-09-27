import logging


logging.basicConfig(
    filename="operations.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


def log_operation(message):
    logging.info(message)