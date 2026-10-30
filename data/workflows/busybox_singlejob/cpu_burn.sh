#!/bin/sh
set -e

DURATION="${RUN_SECONDS:-60}"

echo "Starting CPU burn for ${DURATION} seconds..."
end=$(($(date +%s) + DURATION))

while [ "$(date +%s)" -lt "$end" ]; do
    # Tight arithmetic loop — keeps one core at 100%
    i=0
    while [ "$i" -lt 100000 ]; do
        i=$((i + 1))
    done
done

echo "Done after ${DURATION} seconds."
