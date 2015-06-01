#!/bin/sh

### BEGIN INIT INFO
# Provides:          lirc-controller
# Required-Start:    $all
# Required-Stop:     mpd
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Extended remote controller daemon 
# Description:       Extended remote controller daemon
### END INIT INFO

. /lib/lsb/init-functions

PATH=/sbin:/bin:/usr/sbin:/usr/bin
NAME=lirc-controllerd
DESC="Extended remote controller daemon"
DAEMON="/usr/bin/python"
ARGS="/root/scripts/mpd/lirc-controller/src/app.py --conf /root/scripts/mpd/lirc-controller/resources/configuration/prod/configuration-basic.cfg --xml /root/scripts/mpd/lirc-controller/resources/configuration/prod/configuration-basic.xml --log /root/scripts/mpd/lirc-controller/resources/configuration/prod/logging.cfg"
PIDFILE=/var/run/lirc-controllerd/pid

start() {
	log_daemon_msg "Starting $DESC" "$NAME"
	PIDDIR=$(dirname "$PIDFILE")
	if [ ! -d "$PIDDIR" ]; then
		mkdir -m 0755 $PIDDIR
	fi
	# start deamon
	start-stop-daemon --start --background --make-pidfile --quiet --oknodo --pidfile "$PIDFILE" \
        --exec "$DAEMON" "$ARGS"	
}

stop() {
	log_daemon_msg "Stopping $DESC" "$NAME"	
	start-stop-daemon --stop --quiet --oknodo --pidfile "$PIDFILE"
	log_end_msg $? 
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 2
        ;;
esac
