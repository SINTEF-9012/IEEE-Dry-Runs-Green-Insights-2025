# Power Stress Multicore pipeline

Created data/workflows/power_stress_multicore/ with three files, mirroring busybox_multicore's structure:

- Dockerfile — Alpine + stress-ng instead of plain busybox.
- power_stress.sh — entrypoint that runs stress-ng with three configurable stressors:
- --cpu --cpu-method matrixprod: floating-point/vector (SIMD) matrix multiply, which actually drives a CPU's power-hungry execution units — unlike the scalar i=$((i+1)) loop in busybox_multicore/cpu_burn_parallel.sh, which stays L1-resident and barely moves power above idle despite showing "100% busy."
-  --vm --vm-bytes 512M: allocates memory blocks larger than typical cache, forcing real DRAM traffic — recruiting the memory subsystem, which a wall-power meter sees but "CPU%" doesn't.
-  --hdd (optional, off by default): sustained disk I/O, echoing the disk-heavy nature of steps like samtools sort/GATK from the NHRF pipeline.
-  pipeline.yaml — same Argo WorkflowTemplate fan-out pattern (replicas, per-pod CPU/memory requests via podSpecPatch) as busybox_multicore/pipeline.yaml, but parameterized for cpu-method, vm-workers-per-pod, vm-bytes-per-worker, etc.



## Scaling Govenor | powersave vs performance

scaling_governor is a host-level, kernel cpufreq setting (/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor), not something namespaced per-container. stress-ng detected all 72 CPUs on the node are set to powersave, and is warning that this may cap performance because:

-  performance governor: pins cores at (near) max frequency whenever busy.
-  powersave governor: still scales frequency up under load (it's dynamic, not stuck at the lowest P-state), but ramps up more conservatively and may not reach max turbo, biasing toward lower energy use over raw throughput.

### Why this is relevant to your experiment

This directly interacts with the question you were investigating earlier: if the governor keeps clock/voltage lower under powersave, the matrixprod/vm stressors may draw less power and run slower than they would under performance — potentially dampening the very power-draw signal you built power_stress_multicore to produce. So if the goal is to elicit a clear, comparable wall-power surge, this setting works against you.

### Can you fix it from the pod?

Generally, no — not cleanly:
-  scaling_governor is global to the physical host, shared across all 72 cores and every other tenant/workload on that "mainframe," not scoped to your pod's 4 requested cores.
-  Changing it requires root on the host itself, or a privileged: true pod with hostPID and a hostPath mount of /sys — and even then, the change persists node-wide after your job ends, affecting other users on a shared research machine. That's likely not appropriate to bake into the workflow itself without coordinating with whoever administers it.

### Recommended options

1. Leave it as-is and treat this as a known confound to note in your methodology — you're measuring "power draw under the node's default governor," which is arguably the realistic/representative setting anyway (NHRF ran under the same governor, so the comparison stays apples-to-apples).
2. If you have host/root access to the mainframe (outside Kubernetes), set it once before running experiments:
bash
   and revert to powersave afterward if it's a shared machine.
3. Don't try to do this from inside the Argo pod/container unless you deliberately want a privileged, host-mutating step in the pipeline — it's invasive for a shared resource and unrelated pods would be affected too.


### Log message from job

This message was output when starting the job notifying about the govenor setting on the host system
```bash
stress-ng: info:  [27] note: 72 cpus have scaling governors set to powersave and this may impact performance; setting /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor to 'performance' may improve performance
```


