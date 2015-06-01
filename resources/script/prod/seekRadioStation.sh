#!/bin/sh

BASEDIR=$(dirname $0)
. $BASEDIR/../configuration.sh

SEEK_STATION_NUMBER=$1
echo Seeking radio station by: $SEEK_STATION_NUMBER

MIN_STATION_NUMBER=1
MAX_STATION_NUMBER=5

CURRENT_STATION_NUMBER=$(cat $MPD_LIRC_TMP/current_playlist_number.txt)
echo Current station number: $CURRENT_STATION_NUMBER

STATION_NUMBER=$(($CURRENT_STATION_NUMBER+($SEEK_STATION_NUMBER)))
echo New station number: $STATION_NUMBER 

if [ $STATION_NUMBER -gt $MAX_STATION_NUMBER ]; then
	echo New station number is greater then: $MAX_STATION_NUMBER, resetting to $MIN_STATION_NUMBER  
	STATION_NUMBER=$MIN_STATION_NUMBER
elif [ $STATION_NUMBER -lt $MIN_STATION_NUMBER ]; then
	STATION_NUMBER=$MAX_STATION_NUMBER
	echo New station number is lower then: $MIN_STATION_NUMBER, resetting to $MAX_STATION_NUMBER
fi

echo Loading new radio station number: $STATION_NUMBER

sh /root/scripts/mpd_v2/commands/utils/loadAndPlayRadio.sh $STATION_NUMBER
