# Cloud VM Experiments

This directory contains data from initial experiments conducted on a cloud virtual machine (VM) environment using CarbonTracker for environmental impact measurement.

## Overview

These experiments represent the preliminary phase of the research, where different configurations of the NHRF bioinformatics pipeline were tested to understand their energy consumption and CO2 emissions patterns.

## Experimental Setup

- **Environment**: Cloud VM
- **Measurement tool**: CarbonTracker (software-based energy/CO2 monitoring)
- **Pipeline configurations**: Multiple configurations including base1, base2, and optimized variants

## Directory Structure

### Individual Runs (run1-run4)

Each run directory contains:
- `data/` - Raw CarbonTracker measurement data
- `results/` - Processed statistics and metrics
- `screenshots/` - Visual documentation of experiments
- `*.gnuplot` - Gnuplot scripts for individual run visualization

### Aggregated Results (`results/`)

- `detailed_stats_*.dat` - Detailed statistics for each configuration
- `totals.dat` - Aggregated totals across all runs
- `totals_stats.dat` - Statistical summary of totals
- `*.png` - Generated visualization plots

### Analysis Scripts (`scripts/`)

- `compute-detailed-stats.sh` - Computes detailed statistics from raw data
- `compute-totals-for-runs.sh` - Aggregates total metrics across runs
- `compute-totals-stats.sh` - Computes statistical summaries
- `co2-energy.gnuplot` - Generates CO2 and energy comparison plots
- `duration.gnuplot` - Generates pipeline duration plots
- `plot_energy_comparison.gnuplot` - Creates energy comparison visualizations

## Pipeline Configurations

### base1
Straightforward implementation following the pipeline diagram directly.

### base2
Optimized version with:
- Parallelized trimming of samples
- Better memory optimization in alignment (`bwa mem -t 6 -K 100000000`)
- Parallelized mark duplicates step
- Parallelized base quality score step

### optimized
Hybrid configuration combining the best-performing steps from base1 and base2:
1. base2 Trimming
2. base1 Alignment
3. base2 Mark Duplicates
4. base2 Base Quality Score

## Usage

To regenerate the plots from the raw data:

```bash
cd scripts
./compute-detailed-stats.sh
./compute-totals-for-runs.sh
./compute-totals-stats.sh
gnuplot co2-energy.gnuplot
gnuplot duration.gnuplot
```

## Notes

- These cloud VM experiments were conducted before the mainframe experiments
- Results from these experiments informed the design of the mainframe experimental setup
- For the complete dual-measurement approach (CarbonTracker + hardware monitoring), see the `../mainframe/` directory
