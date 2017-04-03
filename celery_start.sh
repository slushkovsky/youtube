#!/usr/bin/env bash
mkdir -p $HOME/celery/run/
mkdir -p $HOME/celery/log/

celery multi start yt_platform_worker -A youtube_platform beat --pidfile="$HOME/celery/run/%n.pid" --logfile="$HOME/celery/log/%n%I.log"
