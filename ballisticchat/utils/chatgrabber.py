#!env/bin/python

import datetime
import logging
import os
from pprint import pprint
import sys

from pymongo import MongoClient

# Move into directory of this running file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Time in 24 hour format
SHOW_TIME = "00:15"

MONGO_URI = "mongodb://127.0.0.1:27017"
MONGO_DB = "ballistic-chat"
MONGO_COLL = "ballistic-messages"


def query_user():
    print("\nChoose parameters of chat message dump.")

    selections = {}

    tz_cest = datetime.timezone(datetime.timedelta(hours=2), name="CEST")

    # NEED TO IMPLEMENT ALTERNATE WEEKEND SHOWTIME START OF 11AM CEST
    if input("\nUse standard show start time? [Y/n] ") == "n":
        time_input = input("\nInput custom show start time in 24 hour format (hh:mm): ")
        time_formatted = datetime.time(
            hour=time_input.split(":")[0],
            minute=time_input.split(":")[1],
            tzinfo=tz_cest,
        )

    else:
        time_formatted = datetime.time(hour=8, minute=15, tzinfo=tz_cest)

    date_input = input("\nFirst episode (mm/dd/yyyy): ")

    date_split = date_input.split("/")

    date_formatted = datetime.date(
        year=int(date_split[2]),
        month=int(date_split[0]),
        day=int(date_split[1]),
    )

    selections["dt_first"] = datetime.datetime.combine(
        date=date_formatted,
        time=time_formatted,
    )

    if input("\nChoose range of episodes? [y/N] ") == "y":
        date_input = input("\nLast episode (mm/dd/yyyy): ")

        date_split = date_input.split("/")

        date_formatted = datetime.date(
            year=int(date_split[2]),
            month=int(date_split[0]),
            day=int(date_split[1]),
        )

        selections["dt_last"] = datetime.datetime.combine(
            date=date_formatted,
            time=time_formatted,
        )

    else:
        print(f'\nSelecting only single episode. {selections["dt_first"]}')
        selections["dt_last"] = None

    if input("\nSelect specific users? [y/N] ") == "y":
        selections["selected_users"] = [
            user.strip(" ")
            for user in input("\nComma-separated list of users: ").split(",")
        ]

        print("\nSelected the following users for message dump:")
        [print(user) for user in selections["selected_users"]]

    else:
        print(f"\nDumping messages for all users.")
        selections["selected_users"] = None

    if input("\nAre these selections correct? [Y/n]") == "n":
        sys.exit()

    selections["dump_start"] = selections["dt_first"] - datetime.timedelta(minutes=15)
    if selections["dt_last"]:
        selections["dump_end"] = selections["dt_last"] + datetime.timedelta(minutes=120)
    else:
        selections["dump_end"] = selections["dump_start"] + datetime.timedelta(
            minutes=120
        )

    return selections


if __name__ == "__main__":
    data_choices = query_user()

    pprint(data_choices)

    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    coll = db[MONGO_COLL]

    pipeline = [
        {
            "$match": {
                "time": {
                    "$gte": data_choices["dump_start"],
                    "$lte": data_choices["dump_end"],
                }
            }
        },
        {"$sort": {"time": 1}},
        {
            "$project": {
                "name": 1,
                "text": 1,
                # "pic": 0,
                "time": 1,
                "socket": 1,
                "role": 1,
                # "connectedUsers": 0,
                "isSuperChat": 1,
                "hash": 1,
            }
        },
    ]

    agg_result = coll.aggregate(pipeline=pipeline)

    for doc in agg_result:
        pprint(doc)
