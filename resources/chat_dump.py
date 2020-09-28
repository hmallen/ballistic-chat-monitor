import datetime
import logging
from pprint import pprint

from pymongo import MongoClient

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Date in format M/D/YYYY
SHOW_DATE = '9/24/2020'
# Time in 24 hour format
SHOW_TIME = '00:15'

MONGO_URI = 'mongodb://127.0.0.1:27017'
MONGO_DB = 'ballistic-chat'
MONGO_COLL = 'ballistic-messages'


if __name__ == '__main__':
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    coll = db[MONGO_COLL]

    date_raw = SHOW_DATE.split('/')
    time_raw = SHOW_TIME.split(':')

    dt = {
        'year': date_raw[2],
        'month': date_raw[0],
        'day': date_raw[1],
        'hour': time_raw[0],
        'minute': time_raw[1]
    }

    dt_start = datetime.datetime(
        dt['year'],
        dt['month'],
        dt['day'],
        hour=dt['hour'],
        minute=dt['minute']
    )

    dump_start = dt_start - datetime.timedelta(minutes=15)
    dump_end = dt_start + datetime.timedelta(minutes=120)

    pipeline = [
        {'$match': {
            'time': {
                '$gte': dump_start,
                '$lte': dump_end
            }
        }},

        {'$sort': {'time': 1}},

        {'$project': {
            'name': 1,
            'text': 1,
            'pic': 0,
            'time': 1,
            'socket': 0,
            'role': 0,
            'connectedUsers': 0,
            'isSuperChat': 1,
            'hash': 0
        }}
    ]

    agg_result = coll.aggregate(pipeline=pipeline)

    for doc in agg_result:
        pprint(doc)
