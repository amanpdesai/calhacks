import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,  # (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("agents.log"),
        ],
    )
