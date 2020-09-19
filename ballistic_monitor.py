import json
import logging
from pprint import pprint
import sys

import datetime
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

#loop = asyncio.get_event_loop()


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

    def run(self, chat_name, chat_avatar):
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
            logger.debug(f'data: {data}')

        """
        var msg = {name:userObject["name"], text:textToSend, pic: userObject["img"], time:Date.now()};
        socket.emit('chat message', msg);
        """
        # @sio.on('send')
        # async def send_handler(message: str):
        #    logger.debug(f"send message: {data}")

        #    await sio.emit('send message', data['text'])

        async def send_message(message):
            logger.debug(f'message: {message}')

            data = {
                'name': chat_name,
                'text': message,
                'pic': chat_avatar,
                'time': time.time()
            }

            logger.debug(f'data: {data}')

            await sio.emit('chat message', data)

        @sio.on('chat message')
        async def receive_handler(data):
            logger.debug(f"chat message: {data}")
            #print('[@sio.on(\"chat message\")] data:')
            # pprint(data)

            await message_consumer(data)

        async def message_consumer(data):
            data['time'] = datetime.datetime.fromtimestamp(data['time'] / 1000)

            data_serialized = json.loads(json.dumps(
                data, separators=(', ', ': '), cls=NumpyEncoder))

            insert_result = self.mongo_coll.insert_one(data)
            logger.debug(
                f'insert_result.inserted_id: {insert_result.inserted_id}')

        async def start_server(socket_url):
            logger.debug('Entered start_server()')

            await sio.connect(socket_url)

            logger.debug(f'Completed sio.connect(), sid={sio.sid}')

        async def stop_server():
            logger.debug('Entered stop_server()')

            await sio.disconnect()

            logger.debug('Completed sio.disconnect()')

        loop = asyncio.get_event_loop()

        try:
            loop.run_until_complete(start_server(socket_url=self.socket_url))

            loop.run_forever()

        except KeyboardInterrupt:
            logger.info('Exit signal received.')

        except Exception as e:
            logger.exception(f'Unhandled exception: {e}')

        finally:
            logger.info('Shutdown complete.')


if __name__ == '__main__':
    import configparser

    config_path = 'config/settings.conf'

    config = configparser.RawConfigParser()
    config.read(config_path)

    socket_feed = SocketFeed(
        mongo_uri=config['mongodb']['uri'],
        mongo_db=config['mongodb']['db'],
        mongo_collection=config['mongodb']['collection'],
        socket_uri=config['socket.io']['uri'],
        socket_token=config['socket.io']['token']
    )

    socket_feed.run(
        chat_name=config['socket.io']['name'],
        chat_avatar=config['socket.io']['avatar']
    )
