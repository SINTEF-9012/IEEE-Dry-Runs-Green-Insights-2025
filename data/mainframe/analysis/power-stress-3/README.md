# Power Stress 3
Data analysis

Analysis notebooks:
- complete-analysis.ipynb
- comparison-analysis.ipynb
- tapo-analysis-conf-1.ipynb

##
Ran this series of experiments after power-stress-2, where we used a different setting for cpu-per-pod and cpu-workers-per-pod in the stress-ng tool.

In this experiment, we have used:

```yaml
    - name: cpu-per-pod
      value: "30"
    - name: cpu-workers-per-pod
      value: "30"
```

The mainframe computer has 32 vCPUs. So this setting use most of the available CPUs.

## Claude analysis of results
