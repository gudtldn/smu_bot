#!/bin/sh
set -e
chown -R app:app /app/logs
exec gosu app /usr/bin/tini -- "$@"
