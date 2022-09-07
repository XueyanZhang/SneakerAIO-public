#!/usr/bin/env python3

from datetime import datetime
import time
from logger import logger


def pause_util(release_time: str, offset=0):
    """
    release time - time of datetime type
    offset - unit in seconds. Individual bots
    will have different offset to start.
    """
    logger.info('STAGE :: RELEASE TIMER')
    try:
        release = datetime.strptime(release_time, '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logger.info(f'Failed to proess release time. Expected format "YYYY-MM-DD HH:MM:SS" -> {e.__class__.__name__}')
        exit(1)
        return False
    seconds_remaining = (release - datetime.now()).total_seconds()-offset
    logger.info(f'Release time processed successfully.')
    if seconds_remaining < 0:
        # time passed. start right away.
        return True
    logger.info("Timer now starts")
    sleep_duration = 600
    while seconds_remaining > sleep_duration:
        time.sleep(sleep_duration)
        seconds_remaining = (release - datetime.now()).total_seconds()-offset
        logger.info(f"Time mark :: {sleep_duration} seconds passed")
    time.sleep(seconds_remaining)
    return True

# timeTest = datetime.datetime(2021, 3, 24, 6, 0, 0)
# release_timer(timeTest, 0)
