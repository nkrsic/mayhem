# NOte:
#
# This is adapted from the Mayhem tutorials by Lynn Root, see
# copyright below.
# Copyright (c) 2018-2019 Lynn Root
"""
Initial setup - starting point based off of
http://asyncio.readthedocs.io/en/latest/producer_consumer.html

Notice! This requires:
 - attrs==19.1.0

To run:

    $ python part-0/mayhem_1.py

Follow along: https://roguelynn.com/words/asyncio-initial-setup/
"""

import asyncio
from asyncio import Queue

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from enum import Enum
import itertools
import logging
from math import floor
import os
import signal
from statistics import mean

import pprint
PP = pprint.PrettyPrinter(indent=2)
import sys
from uuid import uuid4

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

class SpecialException(Exception):
    pass

async def check_order_book_and_sell_flow(loop):

    # Util constants
    try:
        STRATEGY_INSTANCE_ID = os.environ['BINANCE_SELLBOT_STRATEGY_INSTANCE_ID']
        MONGO_URI = os.environ['NKMG1C_MONGO_URI'] # This is PURPOSELY MISSING FOR NOW!!!!!!
        logging.info("Finished loading environment variables..")

    except KeyError as e:
        print(f"Missing env var: {e}")
        print("Will now raise an exception .. ")
        raise e
        # await shutdown(signal=None, loop=loop)

    await asyncio.sleep(3)


async def simulated_loading_task(delay_seconds=5):
    logging.info("Beginning loading task..")
    await asyncio.sleep(delay_seconds)
    logging.info("Loading task complete.")

async def shutdown(loop, signal=None):
    """Clean up the tasks upon a shutdown signal or exception."""
    if signal:
        logging.info(f"Received exit signal {signal.name}")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    print(f"---- TASK DEBUG -----\n")
    PP.pprint(tasks)

    [t.cancel() for t in tasks]

    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

async def task_with_special_exception():
    await asyncio.sleep(2)
    raise SpecialException("This is a VERY special exception.")

def handle_exception_GLOBAL(loop, context):
    msg = context.get("exception", context["message"])
    logging.error(f"Caught exception: {msg}")
    logging.info("Shutting down..")
    asyncio.create_task(shutdown(loop=loop))


def runDriver():

    loop = asyncio.get_event_loop()

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(loop, signal=s)))
    loop.set_exception_handler(handle_exception_GLOBAL)

    # Add tasks to the asyncio loop
    check_order_book_and_sell_flow_coro = check_order_book_and_sell_flow(loop)
    simulated_loading_task_coro = simulated_loading_task(5)
    task_with_special_exception_coro = task_with_special_exception()

    loop.create_task(simulated_loading_task_coro)
    loop.create_task(check_order_book_and_sell_flow_coro)
    loop.create_task(task_with_special_exception_coro)

    try:
        loop.run_forever()
    finally:
        loop.close()
        print(f"GRACEFULLY SHUTDOWN") # Without global exception handling this is a lie.

if __name__ == "__main__":
    runDriver()
