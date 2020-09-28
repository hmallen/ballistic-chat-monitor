import configparser
import logging
import subprocess

from ballisticchat import socketfeed, monitor, dashboard

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

config = configparser.RawConfigParser()


def launch_modules(config):
    # Socket.io chat feed dump to MongoDB
    #

    # Watch for new messages in db and aggregate
    #

    # Display dashboard in terminal
    #

    pass


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=str,
                        default='./config/settings.conf')
    args = parser.parse_args()
    config_path = args.config

    config.read(config_path)

    try:
        # launch_modules(config)

        socket_proc = subprocess.Popen(['ballisticchat/socketfeed.py'], )

    except KeyboardInterrupt:
        logger.info('Exit signal received.')
