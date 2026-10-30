# Mainframe Experiments

This directory contains data and analysis from experiments conducted on the GIoT group's mainframe computer, using two measurement approaches side by side: SIMPIPE/CarbonTracker (software estimate) and a Tapo P115 smart plug (wall power).

## Overview

The main experiment runs the full NHRF bioinformatics pipeline in six configurations (conf-1 to conf-6). A set of follow-up experiments runs single NHRF steps and synthetic stress workloads to understand why the software estimate and the wall measurement disagree. See [Follow-up Experiments](#follow-up-experiments) and [Findings](#findings).

## Experimental Setup

- **Environment**: Mainframe computer (GIoT group), Kubernetes + Argo Workflows
- **Measurement approaches**:
  1. **SIMPIPE/CarbonTracker**: Software-based energy and CO2 estimate per pipeline step
  2. **Tapo P115 Smart Plug**: Hardware-based power measurement of the whole machine at the socket
- **Configurations tested**: conf-1 through conf-6 (base1, base2, optimized, optimized2, conf-5, conf-6)
- **Workflow definitions**: [`../workflows/`](../workflows/)

## Dual Measurement Approach

### SIMPIPE/CarbonTracker (Software-based)
- Integrated into the pipeline execution
- Reports energy (kWh) and CO2eq (g) per step, using a carbon intensity of ~30 g CO2eq/kWh
- Data stored as `runX.dat` files per experiment (see below)

### Tapo P115 Smart Plug (Hardware-based)
- Physical power measurement at the electrical socket (whole machine, including idle draw and any other load)
- Records average power every 5 minutes
- Retains data for approximately 2 days, so it must be exported soon after each run
- Data exported from the Tapo app as XLS files, stored next to the CarbonTracker data for each experiment

### Derived quantities

| Symbol | Meaning |
|---|---|
| `be` | Baseline energy rate (kWh per 5-minute Tapo sample), from idle periods |
| `BE` | Baseline energy over the pipeline window (`be` × number of samples) |
| `AE` | Absolute Tapo energy over the pipeline window |
| `RE` | Relative Tapo energy above the baseline (`AE − BE`), i.e. the marginal energy caused by the job |
| `SE` | SIMPIPE/CarbonTracker energy |
| `SD` | SIMPIPE duration |

## Directory Structure

```
mainframe/
├── analysis/
│   ├── analysis_functions.py          # Shared analysis functions
│   ├── nhrf/                          # Full NHRF pipeline, conf-1 to conf-6
│   │   ├── tapo-analysis-conf-X.ipynb # Per-configuration Tapo analysis (baseline identification)
│   │   ├── comparison_analysis.ipynb  # Time synchronisation between the two measurements
│   │   ├── complete-analysis.ipynb    # Final results computation
│   │   └── alignment-step-only/       # Notebooks + README for the alignment-only runs
│   ├── power-stress-2/                # Notebooks + README, stress-ng with 4 cores
│   └── power-stress-3/                # Notebooks + README, stress-ng with 30 cores
├── data/
│   ├── carbontracker/                 # Full NHRF pipeline: conf-1/ … conf-6/ (runX.dat + Tapo XLS)
│   ├── alignment-step-only/           # NHRF alignment step only
│   ├── nhrf-trimming-step-only/       # NHRF trimming step only
│   ├── power-stress-2/                # stress-ng, 4 cores
│   ├── power-stress-3/                # stress-ng, 30 cores
│   ├── busybox-v2/                    # Scalar busy-loop CPU burn
│   └── demand-forecasting/            # UPCAST demand forecasting pipeline (8 GB input)
├── results/                           # Generated plots
└── pyproject.toml
```

Each experiment folder under `data/` follows the same layout where the analysis is complete:
- `runX.dat` — SIMPIPE/CarbonTracker output per run (`step start stop duration co2 energy status`)
- `*.xls` — Tapo power export covering the runs
- `surge_time_diffs.dat` — time offsets between the Tapo power surge and the SIMPIPE start/stop
- `final_results.csv`, `final_results_details.csv` — averaged and per-run results from `complete-analysis.ipynb`

## Key Technical Challenges

### Time Synchronization Issue
A significant time offset (~134 minutes) was discovered between CarbonTracker measurements and Tapo smart plug measurements in the full NHRF experiments. This required:
- Manual identification of power surge timing
- Calculation of time differences between measurement systems
- Documentation in `surge_time_diffs.dat` metadata file

### Analysis Methodology
1. Manual baseline identification in Tapo data (5-minute resolution)
2. Power surge detection to correlate with pipeline execution
3. Time difference calculation between measurement systems
4. Final results computed by aligning measurements

### Measurement resolution
With 5-minute Tapo samples, the start and end of a pipeline run cannot be resolved more precisely than one sample. Short steps (e.g. trimming, ~19 minutes) move only 1–3 samples and are barely distinguishable from the baseline.

## Pipeline Configurations

Six configurations of the full NHRF pipeline were tested:
- **conf-1**: base1 — straightforward implementation (bwa alignment)
- **conf-2**: base2 — parallelised and memory-optimised
- **conf-3**: optimized — hybrid of the best steps from base1/base2
- **conf-4**: optimized2 — minimap2 alignment
- **conf-5**: additional configuration
- **conf-6**: additional configuration

See [`../workflows/README.md`](../workflows/README.md) for details.

## Follow-up Experiments

These experiments isolate single steps or synthetic loads so the SIMPIPE estimate can be compared with the wall measurement under controlled CPU usage.

| Experiment | Workload | CPU request | Runs | Date | Status |
|---|---|---|---|---|---|
| `nhrf-trimming-step-only` | NHRF trimming step | 6 | 1 | 2026-10-23 | Tapo response too small to analyse |
| `alignment-step-only` | NHRF alignment step (minimap2 `-t 6`) | 6 | 4 (3 analysed) | 2026-10-29 | Analysed |
| `busybox-v2` | Scalar busy-loop CPU burn, ~1 h | 4 | 4 | 2026-08-11 | Raw data only |
| `power-stress-2` | stress-ng matrixprod, 7 workers, ~3 h | 4 | 4 | 2026-09-28 – 10-01 | Analysed, see note below |
| `power-stress-3` | stress-ng matrixprod, 30 CPU + 2 VM + 1 HDD workers, ~3 h | 30 | 4 | 2026-10-25 | Analysed |
| `demand-forecasting` | UPCAST demand forecasting pipeline, 8 GB input, ~20 min | — | 4 | — | Raw data only |

### NHRF alignment step only

Notebooks: [`analysis/nhrf/alignment-step-only/`](analysis/nhrf/alignment-step-only/)

- Four runs on 2026-10-29, roughly 30 minutes apart, all covered by one Tapo export (`Power.xls`).
- The pipeline logs were lost during the runs, so the SIMPIPE dashboard showed no data. Energy and CO2 were recovered by calling the CarbonTracker API with the recovered CPU metrics.
- **Column swap (fixed):** the recovered table lists `Energy (kWh)` before `CO₂eq (g)`, the opposite of the `runX.dat` header. The first version of the run files therefore reported ~9.2 kWh instead of ~0.31 kWh. The run files now have the correct order.
- **run4 excluded:** the Tapo export starts at 11:30, but run4 ran from 10:33 to 12:08, so its window is only partly covered (RE ≈ 0).

Results (runs 1–3):

| | Average | Std | CV |
|---|---|---|---|
| SE | 0.306 kWh | 0.002 | 0.7 % |
| AE | 0.435 kWh | 0.060 | 14 % |
| RE | 0.104 kWh | 0.060 | 57 % |
| BE | 0.331 kWh (~209 W) | — | — |
| SD | 5700 s (~95 min) | 49 s | — |

| Run | Start–stop | RE (kWh) | AE (kWh) | SE (kWh) |
|---|---|---|---|---|
| run1 | 17:01–18:36 | 0.184 | 0.515 | 0.3075 |
| run2 | 14:57–16:31 | 0.086 | 0.417 | 0.3029 |
| run3 | 12:51–14:27 | 0.042 | 0.373 | 0.3070 |

Observations:
- The Tapo trace contains spikes (290–826 W) that do not line up with the runs, e.g. 600 W and 587 W during run1, a 320–480 W plateau from 18:40 to 19:35 after run1 ended, and 672/814 W at 22:15 with no run active. The machine had other load, which inflates RE, especially for run1. Run3 is the cleanest run, with a marginal power of ~26 W.
- During parts of run2 (15:30–15:55) and run3 (13:10–13:50), wall power falls back to idle (~201–212 W). The workload is not constant (I/O-bound phases or the gap between the tumor and normal alignments), but SE is nearly identical across runs.

### Power stress

Workflow: [`../workflows/power_stress_multicore/`](../workflows/power_stress_multicore/). It runs stress-ng with a floating-point matrix-product CPU stressor and a DRAM-bound VM stressor, so the load actually draws power instead of just showing 100 % CPU.

**power-stress-2** (4 cores, 7 workers): SE ≈ 0.427 kWh per run (~142 W average). Tapo shows ~206 W idle and ~222 W during the job, so the job adds only ~16–23 W at the wall (RE ≈ 0.05 kWh per 3-hour run). See [`analysis/power-stress-2/README.md`](analysis/power-stress-2/README.md).

> **Note:** `data/power-stress-2/final_results.csv` and `final_results_details.csv` currently contain the power-stress-3 numbers (identical values, written two minutes apart on 2026-10-27). They should be regenerated from `analysis/power-stress-2/complete-analysis.ipynb` before use.

**power-stress-3** (30 cores, 30 CPU workers):

| | Average | Std |
|---|---|---|
| SE | 3.202 kWh (~1066 W) | 0.0004 |
| AE | 1.078 kWh (~359 W) | 0.023 |
| RE | 0.444 kWh (~148 W) | 0.070 |
| BE | 0.634 kWh (~211 W) | 0.060 |
| SD | 10814 s (~3 h) | 1 |

- All runs end with status `Error`. The pod memory limit is `2G`, but the VM stressors allocate 2 × 2G and the HDD stressor writes 2G, so workers are probably OOM-killed and restarted and stress-ng exits non-zero. The run still lasts the full 3 hours.
- The host's CPU frequency governor is `powersave` (reported by stress-ng), which limits the real power drawn under load.
- The README states 32 vCPUs, while stress-ng reports 72 CPUs on the node. This is not yet resolved.

## Findings

### 1. SIMPIPE's estimate scales with the number of busy cores

SIMPIPE's implied average power divided by the requested cores is roughly constant across all experiments:

| Experiment | Cores | SE avg. power | Per core |
|---|---|---|---|
| NHRF conf-1 alignment (bwa) | 6 | ~132 W | ~22 W |
| NHRF trimming step only | 6 | ~126 W | ~21 W |
| NHRF conf-4 alignment (minimap2) | 6 | ~175 W | ~29 W |
| Alignment step only (minimap2) | 6 | ~193 W | ~32 W |
| busybox-v2 | 4 | ~142 W | ~35 W |
| power-stress-2 | 4 | ~142 W | ~35 W |
| power-stress-3 | 30 | ~1066 W | ~35 W |

Charging each busy core a fixed 20–35 W is far above this machine's real marginal power per core. Under 30 saturated cores the whole machine rises only from ~211 W to ~359 W. This suggests that SIMPIPE/CarbonTracker uses a utilization- or TDP-based model, not measured power, though this has not yet been confirmed.

### 2. The SE/RE ratio grows with CPU load

| Experiment | SE ÷ RE |
|---|---|
| Full NHRF, conf-1 to conf-3 | 1.2–1.4× |
| Full NHRF, conf-4 to conf-6 | 1.8–3.0× |
| Alignment step only (average of 3 runs) | 2.9× |
| Alignment step only, run3 (least other load) | ~7× |
| power-stress-3 | 7.2× |
| power-stress-2 | ~8.5× |

For the full NHRF pipeline, SE happens to fall between RE and AE because its steps use only 1–6 cores. That should not be read as SE approximating either measurement. When the workload is CPU-heavy, or the measurement is not contaminated by other load, SIMPIPE overestimates the marginal wall energy by about 7–8×.

### 3. SIMPIPE is very repeatable; Tapo RE is not

SE varies by less than 1 % between runs, while RE varies by up to 57 % (alignment step only). The spread in RE comes mainly from other load on the shared machine and from the 5-minute sampling. SE's stability also shows that it does not reflect changes in the actual workload during a run.

### 4. Whole-machine idle power dominates small workloads

The machine idles at ~205–211 W. A 6-core job adds roughly 20–30 W at the wall, so for small pipelines AE is mostly baseline (BE ≈ 76 % of AE in the alignment step only runs). The choice between reporting AE and RE matters more than which pipeline configuration is used.

## Recommendations for Further Runs

1. **Higher-resolution power data:** poll the P115 through its local API every 1–10 s, or use the server's BMC/IPMI power readings, so surges and other load can be identified.
2. **Quiet machine:** run experiments when no other jobs are scheduled, and log what else is running.
3. **Core sweep:** run power-stress with 1, 4, 8, 16 and 30 workers and plot SE and RE against core count to show the per-core scaling directly.
4. **Document SIMPIPE's power model:** confirm whether CarbonTracker uses RAPL, a TDP/utilization model or a fixed per-core coefficient on this host.
5. **Fix the power-stress memory limit:** set `memory-per-pod` above `vm-workers × vm-bytes` plus HDD and overhead (e.g. 8G), so runs finish with `Succeeded`.

## Reproducing the Analysis

### Prerequisites
This analysis uses Python with dependencies managed by `uv`. See `pyproject.toml` for package requirements.

### Setup Environment
```bash
cd data/mainframe
uv sync
```

### Run Analysis
Each experiment has the same three notebooks (in `analysis/nhrf/`, `analysis/nhrf/alignment-step-only/`, `analysis/power-stress-2/` and `analysis/power-stress-3/`), run in this order:

1. **Tapo analysis** (manual baseline identification):
   ```bash
   jupyter notebook tapo-analysis-conf-1.ipynb
   # For the full NHRF pipeline, repeat for conf-2 through conf-6
   ```

2. **Time synchronization analysis**:
   ```bash
   jupyter notebook comparison_analysis.ipynb
   ```
   This generates `surge_time_diffs.dat` with time offsets.

3. **Complete final analysis**:
   ```bash
   jupyter notebook complete-analysis.ipynb
   ```
   Produces `final_results.csv` and `final_results_details.csv` in the experiment's data folder.

## Data Format Notes

### SIMPIPE/CarbonTracker Output
- Format: one `runX.dat` file per run, tab-separated
- Columns: `step start stop duration co2 energy status [output]`; CO2 in g, energy in kWh, duration in seconds
- Check the column order when copying values from the SIMPIPE dashboard or API, which lists energy before CO2. A CO2/energy ratio of ~30 g/kWh confirms the order is correct.

### Tapo Smart Plug Data
- Format: XLS (Excel) files
- Resolution: Average power every 5 minutes
- Retention: ~2 days of historical data
- Note: Data exported after each experimental run; check that the export covers the full window of every run

## Notes

- Virtual environment (`.venv`) is not included in repository
- Notebooks may contain embedded output from analysis
- File paths in notebooks may need adjustment depending on execution environment
- Manual steps were required for baseline identification due to 5-minute measurement resolution
- The mainframe is a shared machine; other load during a run shows up in the Tapo data
