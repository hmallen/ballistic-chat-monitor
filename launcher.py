import configparser
import logging
import multiprocessing

from ballisticchat import socketfeed, monitor

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    config_path = './config/settings.conf'

    config = configparser.RawConfigParser()
    config.read(config_path)

    socket_feed = socketfeed.SocketFeed(
        mongo_uri=config['mongodb']['uri'],
        mongo_db=config['mongodb']['db'],
        mongo_collection=config['mongodb']['collection'],
        socket_uri=config['socket.io']['uri'],
        socket_token=config['socket.io']['token']
    )

    monitor_update = monitor.BallisticMonitor(config_file=config_path)

    try:
        # socket_proc = multiprocessing.Process(
        # target=socket_feed.run, args=tuple())

        monitor_proc = multiprocessing.Process(
            target=monitor_update.start_monitor, args=tuple())

        #socket_proc.daemon = True
        # socket_proc.run()

        #print('AFTER SOCKET_PROC.RUN()')

        monitor_proc.daemon = True
        monitor_proc.run()
        # monitor_update.start_monitor()

        print('AFTER MONITOR_PROC.RUN()')

        socket_feed.run()

    except KeyboardInterrupt:
        logger.info('Exit signal received.')

        # socket_proc.terminate()
        # socket_proc.join()

        #print('AFTER SOCKET_PROC.JOIN()')

        monitor_proc.terminate()
        monitor_proc.join()

        print('AFTER MONITOR_PROC.JOIN()')
