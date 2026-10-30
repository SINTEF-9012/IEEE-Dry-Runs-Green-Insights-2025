# NHRF Alignment step only
Data analysis

Analysis notebooks:
- complete-analysis.ipynb
- comparison-analysis.ipynb
- tapo-analysis-conf-1.ipynb

##
Ran only the alignment step of the NHRF bioinformatics pipeline.

Something happend with the storage of logs during the run, so logs were not available. This caused the frontend dashboard of the result to not show any data.

however, the CPU metrics were recoverable, and warp managed to use this data and call Carbontracker API to get the co2 and energy calculations.

Run	Start time	Finish time	Duration	Energy (kWh)	CO₂eq (g)
nhrf-alignment-wfnqf	17:01:12	18:36:38	1h 35m 26s	0.307501	9.250
nhrf-alignment-rjrn2	14:57:13	16:31:04	1h 33m 51s	0.302937	9.112
nhrf-alignment-sd6bg	12:51:24	14:27:06	1h 35m 42s	0.307037	9.236
nhrf-alignment-ffbtk	10:33:56	12:08:34	1h 34m 38s	0.304664	9.164

## data
Data is stored in `/data/mainframe/data/alignment-step-only`

All of the runs above in run.dat, and each separated into runX.dat.
All runs fall within one Tapo measurement, and the power readings from the smartplug is stored in Power.xls


## Analysis results
=== Analysis of the results ==================================================================

    be  = Baseline Energy rate (kWh per Tapo sample) -- NOT a window total
    BE  = Baseline Energy totaled over the surge/pipeline window (kWh) = be * n_samples
    RE  = Relative Tapo Energy, above baseline, over the surge/pipeline window (kWh)
    AE  = Absolute Tapo Energy over the surge/pipeline window (kWh)
    SE  = SIMPIPE Energy (kWh)
    SD  = SIMPIPE Duration

    Identity: AE == BE + RE  (both expressed as window totals, in kWh)


=== RESULTS FOR conf-1 ==================================================================
    Run :    be       BE       RE       AE     BE+RE      SE       |   SD
-----------------------------------------------------------------------------------------
    run1 : 0.0174   0.3309  0.1843  0.5152  0.5152  0.3075     |   5726.0 seconds (in 1.59 hours)
    run2 : 0.0174   0.3309  0.0857  0.4166  0.4166  0.3029     |   5631.0 seconds (in 1.56 hours)
    run3 : 0.0174   0.3309  0.0420  0.3729  0.3729  0.3070     |   5742.0 seconds (in 1.59 hours)
-----------------------------------------------------------------------------------------
    AVG : 0.0174   0.3309  0.1040  0.4349  0.4349  0.3058     |   5699.7 seconds (in 1.58 hours)
    STD : 0.0000   0.0000  0.0595  0.0595            0.0021     |   49.0 seconds (in 0.01 hours)
=========================================================================================
