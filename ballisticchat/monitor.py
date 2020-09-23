import configparser
import datetime
import logging
from pprint import pprint

from pymongo import MongoClient
import requests

logging.basicConfig()
logger = logging.getLogger('monitor')
logger.setLevel(logging.DEBUG)


class BallisticMonitor:

    def __init__(
        self,
        config_file
    ):
        config = configparser.RawConfigParser()
        config.read(config_file)

        mongo_client = MongoClient(config['mongodb']['uri'])
        mongo_db = mongo_client[config['mongodb']['db']]
        self.msg_coll = mongo_db[config['mongodb']['collection']]
        self.stats_coll = mongo_db[config['mongodb']['stats_collection']]

        self.logstash_uri = config['logstash']['uri']
        self.logstash_auth = (
            config['logstash']['user'], config['logstash']['password'])

    def start_monitor(self):

        def update_stats():
            delta_minute = datetime.timedelta(seconds=60)
            delta_min_ago = datetime.datetime.now() - delta_minute
            logger.debug(f'delta_min_ago: {delta_min_ago}')

            pipeline = [
                {'$match': {'time': {'$gte': delta_min_ago}}},
                {'$group': {'_id': '$name', 'count': {'$sum': 1}}},
                {'$sort': {'count': 1}}
            ]

            # pipeline = [
            #    {'$match': {'time': {'$gte': delta_min_ago}}},
            #    {'$sortByCount': '$name'}
            # ]

            agg_result = self.msg_coll.aggregate(pipeline=pipeline)

            for doc in agg_result:
                """r = requests.post(
                    self.logstash_uri,
                    auth=self.logstash_auth,
                    json=doc
                )"""
                pprint(doc)

        # watch_pipeline = [
        #    {'$match': {'fullDocument.pusherReady': {'$eq': True}}}]
        # with coll.watch(pipeline=watch_pipeline, full_document='updateLookup') as doc_stream:
        #    pass

        logger.info('Starting update monitor.')

        watch_pipeline = [{'$match': {'operationType': 'insert'}}]

        with self.msg_coll.watch(pipeline=watch_pipeline) as doc_stream:
            for doc in doc_stream:
                # update_stats(socket=doc['fullDocument']['socket'])
                update_stats()

        #last_update = time.time()
        # while True:
        #    if time.time() - last_update >= 5:
        #        update_stats()


if __name__ == '__main__':
    monitor = BallisticMonitor(config_file='../config/settings.conf')

    try:
        monitor.start_monitor()

    except KeyboardInterrupt:
        logger.info('Exit signal recieved.')

    except Exception as e:
        logger.exception(e)

    finally:
        logger.info('Exiting.')
