import time
import logging

logger = logging.getLogger(__name__)


def fake_long_running_task():
    counter = 5
    while counter:
        logger.info("my long-running task: %s" % counter)
        time.sleep(1)
        counter -= 1
    return 1
