#!/bin/bash
for line in $( cat /etc/environment ) ; do export $line ; done
exec /usr/bin/uwsgi --ini /airg/overwatchstats/uwsgi.ini

