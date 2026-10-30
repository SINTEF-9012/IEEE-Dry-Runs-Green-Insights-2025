#!/bin/sh
set -e

# How long to stress for, in seconds.
DURATION="${RUN_SECONDS:-60}"

# --- CPU stressor ------------------------------------------------------
# Exercises FPU/vector (SIMD) execution units instead of a cheap
# scalar-integer busy loop. Integer-only, cache-resident loops (see
# busybox_multicore/cpu_burn_parallel.sh) keep a core "busy" from the
# scheduler's point of view but barely move its real power draw above
# idle. matrixprod/fma-style methods drive the wide floating-point/vector
# units that dominate a modern CPU's dynamic power range.
CPU_WORKERS="${CPU_WORKERS:-4}"
CPU_METHOD="${CPU_METHOD:-matrixprod}"

# --- Memory stressor -----------------------------------------------------
# Allocates blocks larger than the CPU's cache so reads/writes actually hit
# the memory controller/DRAM, instead of staying resident in L1/L2 like a
# tiny busy loop. This recruits the memory subsystem, which a wall-power
# meter sees but "CPU%" alone does not.
VM_WORKERS="${VM_WORKERS:-2}"
VM_BYTES="${VM_BYTES:-512M}"
VM_METHOD="${VM_METHOD:-all}"

# --- Optional disk stressor ----------------------------------------------
# Sustained read/write I/O, similar in spirit to the disk-heavy steps of
# real pipelines (e.g. samtools sort, GATK MarkDuplicates). Disabled by
# default since it needs writable ephemeral storage.
HDD_WORKERS="${HDD_WORKERS:-0}"
HDD_BYTES="${HDD_BYTES:-256M}"

echo "Starting power-hungry stress for ${DURATION}s:"
echo "  cpu: ${CPU_WORKERS} worker(s), method=${CPU_METHOD}"
echo "  vm:  ${VM_WORKERS} worker(s), ${VM_BYTES} each, method=${VM_METHOD}"
if [ "${HDD_WORKERS}" -gt 0 ]; then
    echo "  hdd: ${HDD_WORKERS} worker(s), ${HDD_BYTES} each"
fi

# shellcheck disable=SC2086
set -- stress-ng \
    --cpu "${CPU_WORKERS}" --cpu-method "${CPU_METHOD}" \
    --vm "${VM_WORKERS}" --vm-bytes "${VM_BYTES}" --vm-method "${VM_METHOD}" --vm-keep \
    --timeout "${DURATION}s" \
    --metrics-brief

if [ "${HDD_WORKERS}" -gt 0 ]; then
    set -- "$@" --hdd "${HDD_WORKERS}" --hdd-bytes "${HDD_BYTES}" --temp-path /tmp
fi

exec "$@"
