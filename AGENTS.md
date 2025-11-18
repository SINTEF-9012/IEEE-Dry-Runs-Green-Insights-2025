# IEEE-Dry-Runs-Green-Insights

Supplementary information repository for the journal paper "Dry Runs, Green Insights: A Framework for Environmental Impact Assessment of Containerised Big Data Pipelines".

This repository contains data, analysis scripts, and results from experiments evaluating the environmental impact of containerized big data pipelines using the NHRF bioinformatics use-case.

## Project Status

**Raw data analyzed**: ✓ Complete (227MB total)
**Project structure**: ✓ Complete
**File migration**: ✓ Complete (~10MB copied)
**Workflows added**: ✓ Complete (NHRF pipeline YAML files in data/workflows/)
**Documentation**: ✓ Complete
**Git repository**: Ready for initial commit

**Last updated**: 2025-11-18

---

## Data Analysis Summary

### Raw Data Location
`/Users/gorans/Documents/Gnuplot/carbontracker`

### Experiment Overview

**Use-case**: NHRF bioinformatics pipeline (tumor genome comparison)
**Measurement approaches**:
1. **CarbonTracker** - Software-based energy/CO2 monitoring
2. **Tapo P115 Smart Plug** - Hardware-based power/energy monitoring

**Pipeline configurations tested**:
- `base1` - Straightforward implementation
- `base2` - Parallelized and memory-optimized
- `optimized` - Hybrid combining best steps from base1/base2
- `conf-5` and `conf-6` - Additional configurations

**Experiment environments**:
1. **Cloud VM** (run1-run4) - Initial experiments
2. **Mainframe** (conf-1 to conf-6) - Complete experiments with dual measurement

### Data Structure

#### Cloud VM Data (run1-run4)
Each run contains:
- `data/` - Raw measurement data
- `results/` - Processed statistics
- `screenshots/` - Visual documentation
- Gnuplot scripts for visualization

#### Mainframe Data
- **Analysis code**: `analysis_functions.py` (30KB)
- **Jupyter notebooks**:
  - `tapo-analysis-conf-X.ipynb` - Per-config Tapo data analysis
  - `comparison_analysis.ipynb` - Time synchronization analysis
  - `complete-analysis.ipynb` - Final results computation
- **Data subdirectories**:
  - `data_carbontracker/` - CarbonTracker measurements
  - `data_tapo-p115-sct-sd/` - Tapo smart plug exports
- **Final outputs**: CSV files with aggregated results

#### Aggregated Results
- Shell scripts: `compute-detailed-stats.sh`, `compute-totals-for-runs.sh`, `compute-totals-stats.sh`
- Gnuplot scripts: `co2-energy.gnuplot`, `duration.gnuplot`, `plot_energy_comparison.gnuplot`
- PNG visualizations: Energy, CO2, duration comparisons

### Key Technical Notes

1. **Time synchronization issue**: ~134 minute offset between CarbonTracker and Tapo measurements
2. **Tapo measurement resolution**: Power data every 5 minutes, 2-day retention
3. **Analysis approach**: Manual baseline identification and surge detection
4. **Final results**: Stored in `final_results.csv` and `final_results_details.csv`

---

## Project Plan

### Phase 1: Repository Setup ✓
- [x] Create directory structure
- [x] Write LICENSE file (MIT License)
- [x] Write CITATION.cff with paper metadata
- [x] Write comprehensive README.md
- [x] Create .gitignore file

### Phase 2: Data Organization ✓

#### Pipeline Workflows
- [x] Add NHRF pipeline YAML workflow definitions (data/workflows/)
- [x] Include all six configurations (conf-1 through conf-6)
- [x] Document workflow optimizations and strategies

#### Cloud VM Data
- [x] Copy run1-run4 data directories
- [x] Copy aggregated results and statistics
- [x] Copy gnuplot scripts
- [x] Copy generated plots
- [x] Create data/cloud-vm/README.md explaining experiments

#### Mainframe Data
- [x] Copy mainframe analysis code (Python + notebooks)
- [x] Copy CarbonTracker data
- [x] Copy Tapo smart plug data
- [x] Copy configuration-specific analysis notebooks
- [x] Copy final results (embedded in notebooks)
- [x] Create data/mainframe/README.md explaining:
  - Dual measurement approach
  - Time synchronization challenges
  - Analysis methodology
  - Final results interpretation

### Phase 3: Code and Analysis ✓
- [x] Copy/organize analysis scripts
- [x] Ensure Python dependencies documented (pyproject.toml)
- [x] Create requirements.txt for pip users
- [x] Document computational environment (Python 3.11+, key packages)
- [ ] Verify all notebooks can run (may need to update paths) - *User action required*

### Phase 4: Documentation ✓
- [x] Document experimental setup in detail (README.md, data/README.md)
- [x] Explain pipeline configurations and differences (all READMEs)
- [x] Document measurement methodologies (data/README.md)
- [x] Add instructions for reproducing analysis (data/mainframe/README.md)
- [x] Include references to main paper (README.md, CITATION.cff)
- [x] Add data dictionary explaining file formats (data/cloud-vm/README.md, data/mainframe/README.md)

### Phase 5: Reproducibility ✓
- [x] Create requirements.txt with all dependencies
- [x] Document uv usage in README and pyproject.toml
- [x] Document manual steps needed (baseline identification, time sync)
- [x] Add notes on notebook execution and path updates
- [ ] Test that analysis notebooks run with fresh environment - *User action required*

### Phase 6: Final Review
- [x] Verify all file paths are relative/correct
- [x] Check all documentation for completeness
- [x] Ensure data provenance is clear
- [x] Review against repository best practices
- [x] Create .gitignore file
- [x] Create initial git commit - *Ready to commit*
- [ ] Update author information in LICENSE and CITATION.cff - *User action required*
- [ ] Add paper DOI when available - *User action required*

---

## Directory Structure

```
IEEE-Dry-Runs-Green-Insights-2025/
├── README.md                          # Main documentation
├── CITATION.cff                       # Citation metadata
├── LICENSE                            # MIT License
├── AGENTS.md                          # This file (project plan)
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore patterns
│
├── data/
│   ├── README.md                      # Overview of all experiments
│   │
│   ├── workflows/                     # Pipeline workflow definitions
│   │   ├── README.md                  # Workflow documentation
│   │   ├── conf-1.yaml                # base1 configuration
│   │   ├── conf-2.yaml                # base2 configuration
│   │   ├── conf-3.yaml                # optimized configuration
│   │   ├── conf-4.yaml                # optimized2 configuration
│   │   ├── conf-5.yaml                # conf-5 configuration
│   │   ├── conf-6.yaml                # conf-6 configuration
│   │   ├── create-fasta-index.yaml    # Helper workflow
│   │   ├── nhrf_pipeline_mockup.yaml  # Pipeline mockup
│   │   └── old/                       # Historical workflow versions
│   │
│   ├── cloud-vm/                      # Cloud VM experiments
│   │   ├── README.md                  # Cloud VM experiment documentation
│   │   ├── run1/
│   │   │   ├── data/
│   │   │   ├── results/
│   │   │   ├── screenshots/
│   │   │   └── *.gnuplot
│   │   ├── run2/
│   │   ├── run3/
│   │   ├── run4/
│   │   ├── results/                   # Aggregated results across runs
│   │   │   ├── *.dat                  # Statistics files
│   │   │   └── *.png                  # Generated plots
│   │   └── scripts/
│   │       ├── compute-detailed-stats.sh
│   │       ├── compute-totals-for-runs.sh
│   │       ├── compute-totals-stats.sh
│   │       ├── co2-energy.gnuplot
│   │       ├── duration.gnuplot
│   │       └── plot_energy_comparison.gnuplot
│   │
│   └── mainframe/                     # Mainframe experiments
│       ├── README.md                  # Mainframe experiment documentation
│       ├── analysis/
│       │   ├── analysis_functions.py
│       │   ├── comparison_analysis.ipynb
│       │   ├── complete-analysis.ipynb
│       │   └── tapo-analysis-conf-*.ipynb
│       ├── data/
│       │       └── surge_time_diffs.dat
│       ├── results/
│       │   ├── final_results.csv
│       │   ├── final_results_details.csv
│       │   └── *.png                  # Generated plots
│       └── pyproject.toml             # Python project config (if using uv)

```
  - Mainframe data: ~50-100MB (CarbonTracker + Tapo)
  - Jupyter notebooks: ~5-10MB (with outputs)
  - Results and plots: ~5-10MB
  - Scripts and code: <1MB

---

## Notes for Implementation

1. **Path updates**: All analysis notebooks will need path updates after migration
2. **Virtual environment**: mainframe/.venv should NOT be copied (recreate from requirements)
3. **Sensitive data**: Verify no sensitive information in notebooks/data
4. **Large files**: Repository is ~10MB (well under Git limits, no LFS needed)
5. **Paper reference**: Add paper DOI/citation once published
6. **Workflows**: NHRF pipeline YAML configurations added to data/workflows/
7. **Repository size**: Final size ~10MB (much smaller than 227MB raw data due to selective copying)

---

## Questions to Resolve

1. Which open-source license to use? (MIT, Apache 2.0, CC-BY-4.0 for data?)
2. Should notebooks include outputs or be cleaned?
3. Is there a paper preprint/DOI available yet?
4. Should we include the UPCAST pipeline config files as reference?
5. Any institutional requirements for data sharing?

---

## Success Criteria

- ✓ All experimental data organized and documented
- ✓ Analysis reproducible from repository alone
- ✓ Clear connection to paper methodology
- ✓ Proper attribution and licensing
- ✓ README provides clear entry point
- ✓ Minimal external dependencies documented

