import logging


def get_logger(name, level: int = logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(levelname)-9s %(asctime)s - %(name)-25s| line%(lineno)-4s| %(message)s",
    )
    return logging.getLogger(name)
