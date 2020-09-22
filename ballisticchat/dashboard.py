import configparser
import logging

from pymongo import MongoClient
import requests

logging.basicConfig()
logger = logging.getLogger('dashboard')
logger.setLevel(logging.DEBUG)


class BallisticDashboard:
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

    def start_dashboard(self):
        logger.info('Starting update monitor.')

        watch_pipeline = [{'$match': {'operationType': 'update'}}]

        with self.msg_coll.watch(pipeline=watch_pipeline) as doc_stream:
            for doc in doc_stream:
                # update_stats(socket=doc['fullDocument']['socket'])
                r = requests.post(
                    self.logstash_uri,
                    auth=self.logstash_auth,
                    json=doc
                )


if __name__ == '__main__':
    config_path = '../config/settings.conf'

    dashboard = BallisticDashboard(config_file=config_path)

    try:
        dashboard.start_dashboard()

    except KeyboardInterrupt:
        logger.info('Exit signal received.')

    except Exception as e:
        logger.exception(e)
