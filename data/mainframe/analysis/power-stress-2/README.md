# Power Stress 2
Data analysis

Analysis notebooks:
- complete-analysis.ipynb
- comparison-analysis.ipynb
- tapo-analysis-conf-1.ipynb


Settings for CPU usage:
```yaml
      - name: "cpu-per-pod"
        value: "4000m"
      - name: "cpu-workers-per-pod"
        value: "7"
```


## Claude analysis of results

The numbers (run4, from comparison_analysis.ipynb):

Baseline (idle) whole-machine power, from Tapo: ~205.8 W
Average power during the job window, from Tapo: 222.4 W (peak 229.0 W)
Tapo's total energy over that window: 0.667 kWh
SIMPIPE/Carbontracker's reported energy for the same window: 0.427 kWh → equivalent to an average power of ~142 W
The tell: SIMPIPE's implied average power (~142 W) is lower than the machine's own measured idle floor (~206 W). That's physically impossible if SE were meant to represent total wall-socket power — a running job can't make the whole machine draw less than it does at idle. So SE almost certainly isn't measuring the same thing Tapo measures at all.

Most likely explanation: given the project explicitly pairs "CarbonTracker (software-based)" against "Tapo (hardware-based)" as two different measurement methods, SIMPIPE's energy figure is probably CarbonTracker's internal estimate — typically derived from CPU/GPU package-level counters (Intel RAPL / NVIDIA NVML) when available, or a model/TDP-based fallback when it isn't (which is common inside containers/VMs on a shared machine without privileged access to the MSRs RAPL needs). Either way, that's a narrower quantity than total wall power: it reflects energy attributable to the compute silicon CarbonTracker can see, not the whole physical server (PSU conversion losses, RAM, disks, fans, chipset, NICs, and — if this "mainframe" is multi-tenant — other concurrently running workloads on the same box).

Tapo's RE, by contrast, is the marginal change in the entire machine's wall power caused by this one job, net of everything else happening on that host. If:

the job isn't heavily CPU-bound (e.g. it's I/O- or memory-bound, or only uses a few cores on a big multi-core box), and/or
the machine's non-CPU idle floor is large and roughly constant regardless of this job, and/or
other background load on a shared host already dominates the "baseline" Tapo sees,
then it's entirely plausible that the job barely moves the needle at the wall (+16–23 W here) even while CarbonTracker attributes a much larger chunk of CPU-package energy to it.

So: RE << SE is consistent with "SE measures compute-silicon energy, RE measures whole-system marginal wall energy," not with "RE is wrong." Given this paper's whole premise is comparing software-estimated vs hardware ground-truth energy for containerized pipelines, this divergence is plausibly the finding itself rather than an artifact — it would be worth explicitly checking (if you have access to how SIMPIPE/CarbonTracker was configured for this run) whether it had real RAPL access on this host, or fell back to a model-based estimate, since that would confirm or refute this explanation directly.