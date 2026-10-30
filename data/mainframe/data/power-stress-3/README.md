# power-stress-3

The number of vCPUs on the mainframe computer is 32. 
In this line of runs, we request 30 CPUs and 30 CPU workers per pod, 
so that for every core the pod is granted gets a busy worker.

```yaml
    - name: cpu-per-pod
      value: "30"
    - name: cpu-workers-per-pod
      value: "30"
```

Why were not requesting 32 CPUs is to ensure that the job will be scheduled to run. The system requires some CPUs for dedicated tasks.


