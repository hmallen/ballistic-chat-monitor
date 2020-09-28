#!../env/bin/python

import configparser
import datetime
import logging
from pprint import pprint

from pymongo import MongoClient
import requests

logging.basicConfig()
logger = logging.getLogger('dashboard')
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

        self.dash_coll = mongo_db[config['mongodb']['dashboard_collection']]

        self.dash_length = int(config['dashboard']['length'])
        self.flag_threshold = int(config['dashboard']['flag_threshold'])

    def start_monitor(self):

        def print_dashboard(data):

            def build_message(msg_list):
                msg = f'\nFlagged Users (>={self.flag_threshold} msg/min):\n'
                msg += ', '.join(msg_list)
                # msg = msg.rstrip(', ')

                return msg

            print('------------ msg/min ------------\n')

            user_doc = data['fullDocument']['users']

            for x in range(0, (self.dash_length + 1)):
                if x >= len(user_doc):
                    print()

                else:
                    print(
                        f"{str(user_doc[x]['count']).ljust(2, ' ')} - {user_doc[x]['name']}")

                    if user_doc[x]['count'] >= self.flag_threshold:
                        if user_doc[x]['name'] not in flagged_users:
                            flagged_users.append(user_doc[x]['name'])

            print(build_message(flagged_users))

            print('\n---------------------------------\n')

        logger.info('Starting dashboard monitor.')

        flagged_users = []

        watch_pipeline = [{'$match': {'operationType': 'update'}}]

        with self.dash_coll.watch(pipeline=watch_pipeline, full_document='updateLookup') as doc_stream:
            for doc in doc_stream:
                # ['fullDocument']['users'].sorted(key='count'))
                # pprint(doc['fullDocument']['users'])

                print_dashboard(doc)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=str,
                        default='../config/settings.conf')
    args = parser.parse_args()
    config_path = args.config

    monitor = BallisticMonitor(config_file=config_path)

    try:
        monitor.start_monitor()

    except KeyboardInterrupt:
        logger.info('Exit signal recieved.')

    except Exception as e:
        logger.exception(e)

    finally:
        logger.info('Exiting.')
