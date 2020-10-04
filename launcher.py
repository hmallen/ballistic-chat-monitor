# import os
import logging
import subprocess
import sys

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def launch_modules():
    # Socket.io chat feed dump to MongoDB
    #

    # Watch for new messages in db and aggregate
    #

    # Display dashboard in terminal
    #
    socket_proc = subprocess.Popen(
        [
            # "env/bin/python",
            "home/hunter/src/ballistic-chat-monitor/ballisticchat/socketfeed.py",
        ]
    )
    monitor_proc = subprocess.Popen(
        [
            # "env/bin/python",
            "/home/hunter/src/ballistic-chat-monitor/ballisticchat/monitor.py",
        ]
    )
    dash_proc = subprocess.Popen(
        [
            # "env/bin/python",
            "/home/hunter/src/ballistic-chat-monitor/ballisticchat/dashboard.py",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out, err = dash_proc.communicate()
    # logger.debug(f'out: {out}')
    # logger.debug(f'err: {err}')


if __name__ == "__main__":
    try:
        # launch_modules()

        socket_proc = subprocess.Popen(
            [
                # "env/bin/python",
                "home/hunter/src/ballistic-chat-monitor/ballisticchat/socketfeed.py"
            ]
        )

        monitor_proc = subprocess.Popen(
            [
                # "env/bin/python",
                "/home/hunter/src/ballistic-chat-monitor/ballisticchat/monitor.py"
            ]
        )

        dash_proc = subprocess.Popen(
            [
                # "env/bin/python",
                "/home/hunter/src/ballistic-chat-monitor/ballisticchat/dashboard.py"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        out, err = dash_proc.communicate()

        logger.debug("End of main try clause.")

    except KeyboardInterrupt:
        logger.info("Exit signal received.")
        sys.exit()

    except Exception as e:
        logger.exception(e)
