# Tapo p115 smart plug energy measurements vs simpipe/carbontracker energy measurements
###########################################################################################

# Set terminal and output
set terminal pngcairo size 1000,600 enhanced font 'Linux Libertine Bold,12'
set output 'energy_comparison.png'

set datafile separator ','

# Set title and labels
set xlabel "TAPO Energy (kWh)"
set ylabel "SIMPIPE/Carbontracker Energy (kWh)"

# Computed average baseline energy of the "mainframe" computer mesured by the Tapo device.
# bear in mind that the computed energies are the sum of energy over the course of the pipeline/workflow
# the baseline energy is the average instantaneous energy of the tapo devices (for one timestamp)

# Remove the PUE factor from the  simpipe/carbontracker results by multiplying with 1/PUE
PUE_2023 = 1.58
shift = 1/PUE_2023


set grid
set key inside top left spacing 2

# Plot the data using xyerrorbars
# columns:
#  1 conf
#  2 tapo_baseline_energy_avg
#  3 tapo_baseline_energy_std
#  4 tapo_absolute_energy_avg
#  5 tapo_absolute_energy_std
#  6 tapo_relative_energy_avg
#  7 tapo_relative_energy_std
#  8 simpipe_energy_avg
#  9 simpipe_energy_std
# 10 simpipe_duration_avg
# 11 simpipe_duration_std
plot \
     './mainframe/data_carbontracker/final_results.csv' using 6:($8*shift):7:9 every ::1::1 with xyerrorbars lc rgb "#1f77b4" lw 2 ps 3 pt 4 title "conf-1", \
     ''                                                 using 6:($8*shift):7:9 every ::2::2 with xyerrorbars lc rgb "#ff7f0e" lw 2 ps 3 pt 6 title "conf-2", \
     ''                                                 using 6:($8*shift):7:9 every ::3::3 with xyerrorbars lc rgb "#2ca02c" lw 2 ps 3 pt 7 title "conf-3", \
     ''                                                 using 6:($8*shift):7:9 every ::4::4 with xyerrorbars lc rgb "#ff0ebb" lw 2 ps 3 pt 8 title "conf-4", \
     ''                                                 using 6:($8*shift):7:9 every ::5::5 with xyerrorbars lc rgb "#0efffb" lw 2 ps 3 pt 9 title "conf-5", \
     ''                                                 using 6:($8*shift):7:9 every ::6::6 with xyerrorbars lc rgb "#297e75" lw 2 ps 3 pt 2 title "conf-6", \
     x with lines lt 1 lc rgb "black" lw 1 dt 2 title ""

