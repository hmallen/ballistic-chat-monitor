import os
import logging
from pprint import pprint
import json

# {'_id': ObjectId('5fab98947516386200423ecc'), 'name': 'John Cafarelli', 'text': 'Have to be a little crazy to be in crypto lol love it', 'time': '2020-11-11T00:53:56.651000', 'translation': '', 'translation_info': {}}

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

target_users = [
    "Chezi Rubinstein",
    "GEBELEIZIS",
    "roni moshe",
    "Erez Atia",
    "Hunter Allen",
    "Nate Lovell",
]

INPUT_FILE = "chat_111120_geb-orig.jsonl"


if __name__ == "__main__":
    with open(INPUT_FILE, "r") as messages_json:
        for line in messages_json.readlines():
            try:
                # print(f"\nLine: {line}")
                msg = json.loads(line)
                # if msg["name"] in target_users:
                with open("chat_translated_111120-full.txt", "a+") as dump_file:
                    dump_file.write(f'\n\n{msg["name"]} | {msg["text"]}')
                    dump_file.write(f'\nTranslation: {msg["translation"]}')

                print(f'\n{msg["name"]} | {msg["text"]}')
                print(f'Translation: {msg["translation"]}')
            except Exception as e:
                # logger.exception(f"Exception: {e}")
                continue
