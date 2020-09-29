import configparser
import logging
import subprocess
import sys

# from ballisticchat import socketfeed, monitor, dashboard

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

config = configparser.RawConfigParser()


def launch_modules():
    # Socket.io chat feed dump to MongoDB
    #

    # Watch for new messages in db and aggregate
    #

    # Display dashboard in terminal
    #
    socket_proc = subprocess.Popen(['./dashboard/socketfeed.py'])
    monitor_proc = subprocess.Popen(['./dashboard/monitor.py'])
    dash_proc = subprocess.Popen(
        ['./dashboard/dashboard.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    out, err = dash_proc.communicate()
    #logger.debug(f'out: {out}')
    #logger.debug(f'err: {err}')


if __name__ == '__main__':
    # import argparse

    # parser = argparse.ArgumentParser()
    # parser.add_argument('--config', '-c', type=str,
    #                    default = './config/settings.conf')
    # args = parser.parse_args()
    # config_path = args.config

    # config.read(config_path)

    try:
        launch_modules()

    except KeyboardInterrupt:
        logger.info('Exit signal received.')
        sys.exit()

    except Exception as e:
        logger.exception(e)
