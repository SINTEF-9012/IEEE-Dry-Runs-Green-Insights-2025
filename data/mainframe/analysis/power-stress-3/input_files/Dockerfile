FROM alpine:3.20

RUN apk add --no-cache stress-ng

# CPU: number of workers and stress-ng "method". matrixprod drives the
# floating-point/vector (SIMD) execution units, which dominate a modern
# CPU's real dynamic power range far more than a scalar-integer busy loop
# (see ../busybox_multicore/cpu_burn_parallel.sh) ever does, despite both
# reporting ~100% "CPU busy" to the scheduler.
ENV RUN_SECONDS=10800
ENV CPU_WORKERS=4
ENV CPU_METHOD=matrixprod

# Memory: number of workers and bytes allocated per worker. Sized to exceed
# typical L2/L3 cache so reads/writes actually hit the memory
# controller/DRAM -- real, wall-visible power draw -- instead of staying
# resident in L1 like a tiny busy loop.
ENV VM_WORKERS=2
ENV VM_BYTES=512M
ENV VM_METHOD=all

# Optional disk I/O stressor (0 = disabled). Mirrors the disk-heavy nature
# of real pipelines (e.g. samtools sort, GATK) that a pure CPU/memory
# stressor still doesn't capture.
ENV HDD_WORKERS=0
ENV HDD_BYTES=256M

COPY power_stress.sh /power_stress.sh
RUN chmod +x /power_stress.sh

CMD ["/power_stress.sh"]
