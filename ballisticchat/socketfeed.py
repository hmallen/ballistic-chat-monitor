#!env/bin/python

import configparser
import datetime
import json
import logging
import os
from pprint import pprint
import sys
import time

import asyncio
import socketio

from pymongo import MongoClient
from numpyencoder import NumpyEncoder

# Move into directory of this running file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Setup Logging
logging.basicConfig()
logger = logging.getLogger("socketfeed")
# logger = logging.getLogger('socketio')
logger.setLevel(logging.DEBUG)

config = configparser.RawConfigParser()


class SocketFeed:
    def __init__(self, config_file):
        config.read(config_file)

        # MongoDB Client
        mongo_client = MongoClient(config["mongodb"]["uri"])
        mongo_db = mongo_client[config["mongodb"]["db"]]
        self.msg_coll = mongo_db[config["mongodb"]["message_collection"]]

        # Socket.io Client
        self.socket_url = f"{config['socket.io']['uri']}{config['socket.io']['token']}"

    def run(self):
        # Socket.io Client
        sio = socketio.AsyncClient(logger=logger, engineio_logger=logger)

        ## Socket.io Event Handlers ##

        @sio.on("connect")
        async def connect_handler():
            logger.info("Connected.")

        @sio.on("disconnect")
        async def disconnect_handler():
            logger.info("Disconnected.")

            loop.stop()

        @sio.on("history")
        async def history_handler(data):
            # logger.debug(f'data: {data}')
            pass

        @sio.on("chat message")
        async def receive_handler(data):
            logger.debug(f"chat message: {data}")

            await message_consumer(data)

        async def message_consumer(message):
            # Generate hash from time before converting to datetime object
            if message["isSuperChat"] is False:
                hashable = message["socket"]

            else:
                hashable = message["token"]

            message["hash"] = hash((hashable, message["time"]))

            msg_serialized = json.loads(
                json.dumps(message, separators=(", ", ": "), cls=NumpyEncoder)
            )

            msg_serialized["time"] = datetime.datetime.fromtimestamp(
                msg_serialized["time"] / 1000
            )

            insert_result = self.msg_coll.insert_one(msg_serialized)

            logger.debug(f"insert_result.inserted_id: {insert_result.inserted_id}")

        async def start_feed(socket_url):
            logger.debug("Entered start_feed()")

            await sio.connect(socket_url)

            logger.debug(f"Completed sio.connect(), sid={sio.sid}")

        loop = asyncio.get_event_loop()

        loop.run_until_complete(start_feed(socket_url=self.socket_url))

        loop.run_forever()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", type=str, default="../config/settings.conf")
    args = parser.parse_args()
    config_path = args.config

    socket_feed = SocketFeed(config_file=config_path)

    try:
        socket_feed.run()

    except KeyboardInterrupt:
        logger.info("Exit signal received.")

    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")

    # finally:
    #    logger.info('Shutdown complete.')
