#!env/bin/python

import argparse
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
SHOW_TIME = "06:15"

MONGO_URI = "mongodb://127.0.0.1:27017"
MONGO_DB = "ballistic-chat"
MONGO_COLL = "ballistic-messages"

parser = argparse.ArgumentParser()
parser.add_argument(
    "-t",
    "--time",
    default=SHOW_TIME,
    help="Use altername show start time.",
)
parser.add_argument(
    "-f",
    "--first",
    help="First show date (mm/dd/yyyy)",
)
parser.add_argument(
    "-l",
    "--last",
    help="Last show date if returning range (mm/dd/yyyy)",
)
parser.add_argument(
    "-u",
    "--users",
    help="Comma separated list of users for message dump.",
)
parser.add_argument(
    "-y",
    "--yes",
    action="store_true",
    help="Skip confirmation and immediately proceed with message dump.",
)
args = parser.parse_args()


def query_user():
    print("\nChoose parameters of chat message dump.")

    selections = {}

    tz_query = datetime.timezone(datetime.timedelta(hours=2), name="CEST")
    # tz_query = datetime.timezone.utc

    # NEED TO IMPLEMENT ALTERNATE WEEKEND SHOWTIME START OF 11AM CEST
    if args.time:
        time_input = args.time

    elif input("\nUse standard show start time? [Y/n] ") == "n":
        time_input = input("\nInput custom show start time in 24 hour format (hh:mm): ")

    else:
        time_input = SHOW_TIME

    time_split = time_input.split(":")

    time_formatted = datetime.time(
        hour=int(time_split[0]),
        minute=int(time_split[1]),
        tzinfo=tz_query,
    )

    if args.first:
        date_input = args.first

    else:
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

    if args.last:
        date_input = args.last

    elif input("\nChoose range of episodes? [y/N] ") == "y":
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

    if args.users:
        user_list = args.users

    elif input("\nSelect specific users? [y/N] ") == "y":
        user_list = input("\nComma-separated list of users: ")

    else:
        print(f"\nDumping messages for all users.")
        user_list = None

    if user_list:
        selections["selected_users"] = [
            user.strip(" ") for user in user_list.split(",")
        ]

        print("\nSelected the following users for message dump:")
        [print(user) for user in selections["selected_users"]]

    else:
        selections["selected_users"] = None

    if not args.yes:
        if input("\nAre these selections correct? [Y/n]") == "n":
            sys.exit()

        else:
            print("\nSelections confirmed.")

    selections["dump_start"] = selections["dt_first"] - datetime.timedelta(minutes=15)

    if selections["dt_last"]:
        selections["dump_end"] = selections["dt_last"] + datetime.timedelta(minutes=120)

    else:
        selections["dump_end"] = selections["dump_start"] + datetime.timedelta(
            minutes=120
        )

    return selections


if __name__ == "__main__":
    try:
        data_choices = query_user()

    except KeyboardInterrupt:
        logger.info("Exit signal received.")
        sys.exit()

    except Exception as e:
        logger.exception(e)
        sys.exit(1)

    pprint(data_choices)

    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    coll = db[MONGO_COLL]

    #############################
    # ADD PIPELINE APPEND STEPS #
    #############################

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

    doc_count = agg_result.count_documents()

    for doc in agg_result:
        pprint(doc)

    print(f"\ndoc_count: {doc_count}")
