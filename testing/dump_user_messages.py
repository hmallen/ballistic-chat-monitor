import logging

from pymongo import MongoClient

# Name of user for message dump
CHAT_USER_TARGET = ""

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

mongo = MongoClient("mongodb://localhost:27017")
db = mongo["ballistic-chat"]
coll = db["ballistic-messages"]


if __name__ == "__main__":
    pipeline = [
        {"$match": {"name": CHAT_USER_TARGET}},
        {"$project": {"name": 1, "text": 1, "time": 1}},
        {"$sort": {"time": 1}},
    ]

    user_messages = coll.aggregate(pipeline=pipeline)

    msg_count = 0
    for msg in user_messages:
        msg_count += 1

        date_split = str(msg["time"]).split(" ")[0].split("-")
        date = f"{date_split[1]}/{date_split[2]}/{date_split[0]}"
        time = str(msg["time"]).split(" ")[1].split(".")[0]

        # print(f'{msg_count} - {date}|{time}: {msg["text"]}')
        print(f'{date}|{time}: {msg["text"]}')

        if msg_count == 202:
            break
