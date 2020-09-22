import datetime
import json
import logging
from pprint import pprint
import sys
import time

import asyncio
import socketio

from pymongo import MongoClient
from numpyencoder import NumpyEncoder

# Setup Logging
logging.basicConfig()
logger = logging.getLogger(__name__)
#logger = logging.getLogger('socketio')
logger.setLevel(logging.DEBUG)


class SocketFeed:

    def __init__(
        self,
        mongo_uri,
        mongo_db,
        mongo_collection,
        socket_uri,
        socket_token
    ):
        # MongoDB Client
        mongo_client = MongoClient(mongo_uri)
        mongo_db = mongo_client[mongo_db]

        self.mongo_coll = mongo_db[mongo_collection]

        self.socket_url = f"{socket_uri}{socket_token}"

    def run(self, populate_history=True):
        # Socket.io Client
        sio = socketio.AsyncClient(
            logger=logger,
            engineio_logger=logger
        )

        ## Socket.io Event Handlers ##

        @sio.on('connect')
        async def connect_handler():
            logger.info('Connected.')

        @sio.on('disconnect')
        async def disconnect_handler():
            logger.info('Disconnected.')

            loop.stop()

        @sio.on('history')
        async def history_handler(data):
            #logger.debug(f'data: {data}')

            if populate_history is True:
                for msg in data['history']:
                    if msg['isSuperChat'] is False:
                        hashable = msg['socket']

                    else:
                        hashable = msg['token']

                    msg_hash = hash((hashable, msg['time']))

                    matches = self.mongo_coll.count_documents(
                        {'hash': msg_hash})
                    logger.debug(f'matches: {matches}')

                    # if not self.mongo_coll.count_documents({'hash': msg_hash}):
                    # await message_consumer(msg)

                logger.info('Message history pre-population complete.')

        @sio.on('chat message')
        async def receive_handler(data):
            logger.debug(f'chat message: {data}')

            await message_consumer(data)

        async def message_consumer(message):
            # Generate hash from time before converting to datetime object
            if message['isSuperChat'] is False:
                hashable = message['socket']

            else:
                hashable = message['token']

            message['hash'] = hash((hashable, message['time']))

            msg_serialized = json.loads(json.dumps(
                message, separators=(', ', ': '), cls=NumpyEncoder))

            msg_serialized['time'] = datetime.datetime.fromtimestamp(
                msg_serialized['time'] / 1000)

            insert_result = self.mongo_coll.insert_one(msg_serialized)

            logger.debug(
                f'insert_result.inserted_id: {insert_result.inserted_id}')

        async def start_feed(socket_url):
            logger.debug('Entered start_feed()')

            await sio.connect(socket_url)

            logger.debug(f'Completed sio.connect(), sid={sio.sid}')

        loop = asyncio.get_event_loop()

        try:
            loop.run_until_complete(start_feed(socket_url=self.socket_url))

            loop.run_forever()

        except Exception as e:
            logger.exception(f'Unhandled exception: {e}')

        finally:
            logger.info('Shutdown complete.')


if __name__ == '__main__':
    import configparser

    config_path = '../config/settings.conf'

    config = configparser.RawConfigParser()
    config.read(config_path)

    socket_feed = SocketFeed(
        mongo_uri=config['mongodb']['uri'],
        mongo_db=config['mongodb']['db'],
        mongo_collection=config['mongodb']['collection'],
        socket_uri=config['socket.io']['uri'],
        socket_token=config['socket.io']['token']
    )

    socket_feed.run()
