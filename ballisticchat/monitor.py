#!env/bin/python

import configparser
import datetime
import logging
import os
from pprint import pprint
import time

# import requests
from pymongo import MongoClient

# Move into directory of this running file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig()
logger = logging.getLogger("monitor")
logger.setLevel(logging.DEBUG)


class BallisticMonitor:
    def __init__(self, config_file):
        config = configparser.RawConfigParser()
        config.read(config_file)

        mongo_client = MongoClient(config["mongodb"]["uri"])
        mongo_db = mongo_client[config["mongodb"]["db"]]

        self.msg_coll = mongo_db[config["mongodb"]["message_collection"]]
        self.stats_coll = mongo_db[config["mongodb"]["stats_collection"]]

        self.dash_coll = config["mongodb"]["dashboard_collection"]

    def start_monitor(self):
        def update_stats():
            delta_minute = datetime.timedelta(seconds=60)
            delta_min_ago = datetime.datetime.now() - delta_minute
            logger.debug(f"delta_min_ago: {delta_min_ago}")

            pipeline = [
                {"$match": {"time": {"$gte": delta_min_ago}}},
                #    {'$group': {'_id': '$name', 'count': {'$sum': 1}}},
                #    {'$sort': {'count': -1}},
                {"$sortByCount": "$name"},
                {
                    "$group": {
                        "_id": "dashboard",
                        "users": {"$push": {"name": "$_id", "count": "$count"}},
                    }
                },
                {"$merge": self.dash_coll},
            ]

            agg_result = self.msg_coll.aggregate(pipeline=pipeline)

            for doc in agg_result:
                """inserted_id = self.stats_coll.update_one(
                    {'_id': doc['_id']},
                    {'$set': doc},
                    upsert=True
                )"""
                pprint(doc)

        logger.info("Starting update monitor.")

        watch_pipeline = [{"$match": {"operationType": "insert"}}]

        with self.msg_coll.watch(pipeline=watch_pipeline) as doc_stream:
            if doc_stream:
                for doc in doc_stream:
                    update_stats()

                hb_result = self.stats_coll.update_one(
                    {"_id": "heartbeat"}, {"monitor_last": time.time()}, upsert=True
                )
                logger.debug(f"hb_result.modified_count: {hb_result.modified_count}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", type=str, default="../config/settings.conf")
    args = parser.parse_args()
    config_path = args.config

    monitor = BallisticMonitor(config_file=config_path)

    try:
        monitor.start_monitor()

    except KeyboardInterrupt:
        logger.info("Exit signal recieved.")

    except Exception as e:
        logger.exception(e)

    finally:
        logger.info("Exiting.")
