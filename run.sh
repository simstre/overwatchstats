#!/bin/bash
for line in $( cat /etc/environment ) ; do export $line ; done
exec /airg/overwatchstats/localpy/bin/uwsgi --ini /airg/overwatchstats/uwsgi.ini

