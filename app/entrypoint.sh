#!/bin/sh
set -e
python /app/main.py
exec python /app/heartbeat.py
