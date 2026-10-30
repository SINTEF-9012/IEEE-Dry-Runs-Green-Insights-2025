#!/bin/sh
set -e

# How long to burn CPU for, in seconds.
DURATION="${RUN_SECONDS:-60}"
# Number of parallel busy-loop workers to spawn. This should match (or exceed)
# the container's CPU limit/request, since each worker only ever keeps a
# single core busy. This is what the original single-loop cpu_burn.sh got
# wrong: it requested many cores but only ever used one, so overall cluster
# CPU utilization stayed low regardless of how large the request was.
WORKERS="${CPU_WORKERS:-4}"

echo "Starting CPU burn: ${WORKERS} parallel worker(s) for ${DURATION} seconds..."

burn_one() {
    end=$(($(date +%s) + DURATION))
    while [ "$(date +%s)" -lt "$end" ]; do
        # Tight arithmetic loop -- keeps one core at ~100%.
        i=0
        while [ "$i" -lt 100000 ]; do
            i=$((i + 1))
        done
    done
}

pids=""
i=1
while [ "$i" -le "$WORKERS" ]; do
    burn_one &
    pids="${pids} $!"
    i=$((i + 1))
done

# shellcheck disable=SC2086
wait ${pids}

echo "Done after ${DURATION} seconds using ${WORKERS} worker(s)."
