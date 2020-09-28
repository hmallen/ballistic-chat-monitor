import configparser
import datetime
import logging
from pprint import pprint

from pymongo import MongoClient
import requests

from aiohttp import web
import asyncio
import socketio

config_file = '../config/settings.conf'

logging.basicConfig()
logger = logging.getLogger('aiohttp')
logger.setLevel(logging.DEBUG)

config = configparser.RawConfigParser()
config.read(config_file)

mongo_client = MongoClient(config['mongodb']['uri'])
mongo_db = mongo_client[config['mongodb']['db']]

dash_coll = mongo_db[config['mongodb']['dashboard_collection']]

dash_length = int(config['dashboard']['length'])
flag_threshold = int(config['dashboard']['flag_threshold'])

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)


async def start_monitor():
    logger.info('Starting dashboard monitor.')

    watch_pipeline = [{'$match': {'operationType': 'update'}}]

    with dash_coll.watch(pipeline=watch_pipeline, full_document='updateLookup') as doc_stream:
        for doc in doc_stream:
            await sio.emit('my_response', {'data': doc})


async def index(request):
    with open('dashboard.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.event
async def my_event(sid, message):
    await sio.emit('my_response', {'data': message['data']}, room=sid)


@sio.event
async def my_broadcast_event(sid, message):
    await sio.emit('my_response', {'data': message['data']})


@sio.event
async def join(sid, message):
    sio.enter_room(sid, message['room'])
    await sio.emit('my_response', {'data': 'Entered room: ' + message['room']},
                   room=sid)


@sio.event
async def leave(sid, message):
    sio.leave_room(sid, message['room'])
    await sio.emit('my_response', {'data': 'Left room: ' + message['room']},
                   room=sid)


@sio.event
async def close_room(sid, message):
    await sio.emit('my_response',
                   {'data': 'Room ' + message['room'] + ' is closing.'},
                   room=message['room'])
    await sio.close_room(message['room'])


@sio.event
async def my_room_event(sid, message):
    await sio.emit('my_response', {'data': message['data']},
                   room=message['room'])


@sio.event
async def disconnect_request(sid):
    await sio.disconnect(sid)


@sio.event
async def connect(sid, environ):
    await sio.emit('my_response', {'data': 'Connected', 'count': 0}, room=sid)


@sio.event
def disconnect(sid):
    print('Client disconnected')


app.router.add_static('/static', 'static')
app.router.add_get('/', index)


if __name__ == '__main__':
    try:
        sio.start_background_task(start_monitor)
        web.run_app(app)

    except KeyboardInterrupt:
        logger.info('Exit signal recieved.')

    except Exception as e:
        logger.exception(e)

    finally:
        logger.info('Exiting.')
