# Ballistic Chat Monitor

Wondering if you need to bring down the ban hammer on an unruly chat? Chat going so wild, you can't tell who the worst offenders are? With ballistic-chat-monitor, you can monitor messages per second for users in a socket.io chat.

A MongoDB server with replication enabled must be available and host set in config/settings.conf.

Launcher script incomplete. The 3 components must be launched individually.

- socketfeed.py
- monitor.py
- dashboard.py

Each can be run from root directory, assuming a virtualenv has been created in directory named "env". Ex: ./ballistic-chat-monitor/socketfeed.py
