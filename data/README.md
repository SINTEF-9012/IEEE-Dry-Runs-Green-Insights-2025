# Experimental Data

This directory contains all experimental data, analysis code, and results supporting the research paper "Dry Runs, Green Insights: A Framework for Environmental Impact Assessment of Containerised Big Data Pipelines".

## Overview

The experiments evaluate the environmental impact of containerized big data pipelines using the NHRF (Norwegian High-Performance Computing for Research) bioinformatics use-case. The research compares multiple pipeline optimization strategies through comprehensive energy and CO2 monitoring.

## Use Case: NHRF Bioinformatics Pipeline

The NHRF pipeline is a genome comparison workflow designed to identify tumor samples by comparing genome sequences:

**Input Data:**
- Human genome reference: `Homo_sapiens_assembly38.fasta`
- Normal samples: `SRR24141508_1.fastq.gz` and `SRR24141508_2.fastq.gz`
- Tumor samples: `SRR24141497_1.fastq.gz` and `SRR24141497_2.fastq.gz`

**Pipeline Steps:**
1. Get Data
2. Trimming
3. Alignment
4. Mark Duplicates
5. Base Quality Score Recalibration (BSQR)
6. Create FASTA Index (parallel)
7. Create FASTA Dictionary (parallel)

## Experimental Environments

### 1. Cloud VM Experiments (`cloud-vm/`)
- **Purpose**: Initial exploratory experiments
- **Environment**: Cloud virtual machine
- **Measurement**: CarbonTracker (software-based)
- **Runs**: run1 through run4
- **Configurations**: base1, base2, optimized, and variants

### 2. Mainframe Experiments (`mainframe/`)
- **Purpose**: Comprehensive dual-measurement validation
- **Environment**: GIoT group mainframe computer
- **Measurements**: 
  - CarbonTracker (software-based)
  - Tapo P115 Smart Plug (hardware-based)
- **Configurations**: conf-1 through conf-6

## Pipeline Configurations Tested

Six configurations were tested with YAML workflow definitions available in `workflows/`:

### conf-1 (base1)
Straightforward implementation using standard biocontainers and tools in sequence.

### conf-2 (base2)
Parallelized version:
- Parallelized trimming of samples using tool chaining
- Memory-optimized alignment (`bwa mem -t 6 -K 100000000`)
- Parallelized mark duplicates step
- Parallelized base quality score recalibration

### conf-3 (optimized)
Hybrid approach combining best-performing steps:
1. base2 Trimming (parallelized)
2. base1 Alignment (original approach)
3. base2 Mark Duplicates (parallelized)
4. base2 Base Quality Score (parallelized)

### conf-4 (optimized2)
Further optimizations:
- Switched alignment tool from `bwa` to `minimap2`
- Increased CPU allocation for trimming (4 to 6 CPUs)
- Combined FASTA indexing and dictionary creation

### conf-5
Variant of conf-4 using 2 CPUs for all steps.

### conf-6
Variant of conf-4 with 6 CPUs for:
- All tools in the alignment step (including piped samtools)
- Mark duplicates step

See `workflows/README.md` for complete descriptions and optimization rationale.

## Measurement Methodologies

### CarbonTracker (Software-based)
- **Integration**: Embedded in SIMPIPE container orchestration
- **Granularity**: Per-pipeline-step measurements
- **Metrics**: Energy consumption (kWh), CO2 emissions (kg), duration (seconds)
- **Advantages**: High temporal resolution, step-level detail
- **Limitations**: Estimation-based, depends on hardware models

### Tapo P115 Smart Plug (Hardware-based)
- **Integration**: Physical socket between wall and computer
- **Granularity**: Power measurements every 5 minutes
- **Metrics**: Power (W), Energy (kWh)
- **Advantages**: Real hardware measurements, independent validation
- **Limitations**: Lower temporal resolution, 2-day data retention

## Key Findings and Challenges

### Time Synchronization
A ~134 minute offset was discovered between CarbonTracker and Tapo measurements, requiring:
- Manual baseline identification in Tapo data
- Power surge detection for correlation
- Careful time alignment in final analysis

### Measurement Resolution
- CarbonTracker: Sub-second resolution per step
- Tapo P115: 5-minute intervals
- Analysis required surge detection methodology

## Data Volume

- **Total size**: ~227MB
- **Cloud VM data**: ~50-100MB (measurements, screenshots, results)
- **Mainframe data**: ~50-100MB (dual measurements, analysis notebooks)
- **Analysis code**: ~5-10MB (notebooks with outputs)
- **Visualizations**: ~5-10MB (generated plots)

## Directory Structure

```
data/
├── README.md                      # This file
│
├── workflows/                     # Pipeline workflow definitions
│   ├── README.md                  # Workflow documentation
│   ├── conf-1.yaml                # base1 configuration
│   ├── conf-2.yaml                # base2 configuration
│   ├── conf-3.yaml                # optimized configuration
│   ├── conf-4.yaml                # optimized2 configuration
│   ├── conf-5.yaml                # conf-5 configuration
│   └── conf-6.yaml                # conf-6 configuration
│
├── cloud-vm/                      # Cloud VM experiments
│   ├── README.md                  # Cloud VM documentation
│   ├── run1/, run2/, run3/, run4/ # Individual experimental runs
│   ├── results/                   # Aggregated results
│   └── scripts/                   # Analysis and plotting scripts
│
└── mainframe/                     # Mainframe experiments
    ├── README.md                  # Mainframe documentation
    ├── analysis/                  # Python notebooks and functions
    ├── data/                      # Raw measurement data
    │   ├── carbontracker/         # CarbonTracker measurements
    │   ├── tapo/                  # Tapo smart plug data
    │   └── metadata/              # Time sync and other metadata
    ├── results/                   # Final processed results
    └── pyproject.toml             # Python dependencies
```

## Reproducibility

Each subdirectory contains detailed instructions for reproducing the analysis:
- See `workflows/README.md` for pipeline workflow definitions and configurations
- See `cloud-vm/README.md` for cloud VM experiment reproduction
- See `mainframe/README.md` for mainframe experiment reproduction

## Pipeline Workflows

The NHRF pipeline workflow definitions (YAML files) for all six configurations are included in the `workflows/` directory. These YAML files define the complete pipeline structure used with the SIMPIPE container orchestration framework.

## Related Tools

- **SIMPIPE**: Container orchestration framework for data pipelines
- **CarbonTracker**: Energy and CO2 monitoring tool
- **UPCAST**: Framework for containerized pipeline execution

## Citation

If you use this data, please cite the associated paper and this dataset. See the main repository `CITATION.cff` for citation information.
