# Dry Runs, Green Insights: Supplementary Data

Supplementary data and analysis code for the research paper:

**"Dry Runs, Green Insights: A Framework for Environmental Impact Assessment of Containerised Big Data Pipelines"**

## Overview

This repository contains experimental data, analysis scripts, and results from comprehensive experiments evaluating the environmental impact of containerized big data pipelines. The research uses the NHRF bioinformatics use-case to compare different pipeline optimization strategies through dual measurement approaches:

- **CarbonTracker**: Software-based energy and CO2 monitoring
- **Tapo P115 Smart Plug**: Hardware-based power measurement

## Repository Structure

```
.
├── README.md                  # This file
├── CITATION.cff              # Citation information
├── LICENSE                   # MIT License
├── AGENTS.md                 # Project planning documentation
├── requirements.txt          # Python dependencies
│
├── data/                     # Experimental data
│   ├── README.md            # Data overview
│   │
│   ├── workflows/           # Pipeline workflow definitions
│   │   ├── README.md        # Workflow documentation
│   │   ├── conf-1.yaml      # base1 configuration
│   │   ├── conf-2.yaml      # base2 configuration
│   │   ├── conf-3.yaml      # optimized configuration
│   │   ├── conf-4.yaml      # optimized2 configuration
│   │   ├── conf-5.yaml      # conf-5 configuration
│   │   └── conf-6.yaml      # conf-6 configuration
│   │
│   ├── cloud-vm/            # Cloud VM experiments (run1-4)
│   │   ├── README.md
│   │   ├── run1/, run2/, run3/, run4/
│   │   ├── results/         # Aggregated statistics
│   │   └── scripts/         # Analysis scripts
│   │
│   └── mainframe/           # Mainframe experiments (conf-1 to conf-6)
│       ├── README.md
│       ├── analysis/        # Python notebooks
│       ├── data/            # Raw measurements
│       ├── results/         # Final results
│       └── pyproject.toml   # Python config
│
└── docs/                    # Additional documentation
```

## Quick Start

### Viewing the Data

All experimental data is organized in the `data/` directory:
- **Cloud VM experiments**: See `data/cloud-vm/README.md`
- **Mainframe experiments**: See `data/mainframe/README.md`

### Reproducing the Analysis

#### Prerequisites
- Python 3.11 or higher
- uv (recommended) or pip
- Jupyter Notebook

#### Setup with uv (Recommended)

```bash
cd data/mainframe
uv sync
```

#### Setup with pip

```bash
pip install -r requirements.txt
```

#### Running Analysis Notebooks

```bash
cd data/mainframe/analysis
jupyter notebook
```

See `data/mainframe/README.md` for the complete analysis workflow.

## Experimental Overview

### Use Case: NHRF Bioinformatics Pipeline

The NHRF pipeline compares genome samples to identify tumor samples through the following steps:

1. **Get Data** - Download genome reference and sample data
2. **Trimming** - Quality trimming of sequencing reads
3. **Alignment** - Align reads to reference genome
4. **Mark Duplicates** - Identify PCR duplicates
5. **Base Quality Score Recalibration** - Adjust quality scores
6. **Create FASTA Index** - Index reference genome (parallel)
7. **Create FASTA Dictionary** - Create sequence dictionary (parallel)

### Pipeline Configurations

The research tested six configurations with different optimization strategies. Full YAML workflow definitions are available in `data/workflows/`:

- **conf-1 (base1)**: Straightforward implementation using standard biocontainers, sequential tool execution
- **conf-2 (base2)**: Parallelized tool executions using tool chaining
- **conf-3 (optimized)**: Hybrid combining best-performing steps from base1 and base2
- **conf-4 (optimized2)**: Switched alignment from `bwa` to `minimap2`, increased CPU allocation
- **conf-5**: Same as conf-4 but using 2 CPUs for all steps
- **conf-6**: Same as conf-4 but with 6 CPUs for all tools in alignment and mark-duplicates steps

See `data/workflows/README.md` for detailed configuration descriptions and optimization strategies.

### Experimental Environments

#### Cloud VM Experiments
- **Purpose**: Initial exploratory experiments
- **Measurement**: CarbonTracker only
- **Runs**: 4 runs with multiple configurations

#### Mainframe Experiments  
- **Purpose**: Comprehensive dual-measurement validation
- **Measurements**: CarbonTracker + Tapo P115 Smart Plug
- **Configurations**: 6 complete configurations

## Key Findings

### Dual Measurement Validation

The research employed both software-based (CarbonTracker) and hardware-based (Tapo P115) measurements to:
- Validate software-based energy estimations
- Provide real-world power consumption data
- Assess measurement accuracy and reliability

### Technical Challenges

**Time Synchronization**: A ~134 minute offset was discovered between CarbonTracker and Tapo measurements, requiring manual time alignment through power surge detection.

**Measurement Resolution**: Different temporal resolutions (CarbonTracker: sub-second, Tapo: 5 minutes) required specialized analysis techniques.

## Data Volume

- **Total**: ~227MB
- **Cloud VM data**: ~100MB
- **Mainframe data**: ~100MB  
- **Analysis notebooks**: ~10MB
- **Visualizations**: ~10MB

## Citation

If you use this data or code, please cite:

```bibtex
# Paper citation (to be added upon publication)
@article{dryrunsgreen2025,
  title={Dry Runs, Green Insights: A Framework for Environmental Impact Assessment of Containerised Big Data Pipelines},
  author={[Authors]},
  journal={[Journal]},
  year={2025},
  doi={[DOI]}
}

# Dataset citation
# See CITATION.cff for full citation details
```

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Related Projects

- **SIMPIPE**: Container orchestration framework for data pipelines
- **CarbonTracker**: Energy and CO2 monitoring tool
- **UPCAST**: Framework for containerized pipeline execution

## Contact

For questions about this dataset or the research:
- See author information in [CITATION.cff](CITATION.cff)
- Open an issue in this repository

## Acknowledgments

- NHRF for the bioinformatics use-case
- GIoT group for mainframe computational resources
- CarbonTracker developers

## Contributing

If you find issues with the data or analysis, please open an issue or submit a pull request.

---

**Note**: This is supplementary material for an academic research paper. The complete methodology and results interpretation are available in the main paper.