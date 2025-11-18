##############################################################################
# NHRF data pipeline - plot Energy & CO2 barplot
##############################################################################

set terminal pngcairo size 1000,600 enhanced font 'Linux Libertine Bold,12'
set output 'co2-energy.png'

set datafile separator ","

set style fill pattern border rgb "black"

set multiplot
set origin 0,0
set size 1,1
#set boxwidth 0.2
offset = 0.1
set boxwidth offset
set grid ytics

set ylabel "CO2 [g]"
set y2label "Energy [kWh]"
set ytics nomirror
set yrange [0:*]

set y2range [0:0.35]
set y2tics (0, 0.35)

set xlabel "Step"
set xtics rotate by -10
set key inside

set xtics ("Trimming" 1, "Alignment" 2, "Mark Duplicates" 3, "Create FASTA Index" 4, "Create FASTA Dictionary" 5, "Base quality score" 6)
set xrange [0.5:7]

plot \
    'results/detailed_stats_base1.dat' using ($1 - 2*offset):5:6 with boxerrorbars lc rgb "#1f77b4" fs pattern 1 title "conf-1", \
    'results/detailed_stats_base2.dat' using ($1 - 1*offset):5:6 with boxerrorbars lc rgb "#1f77b4" fs pattern 2 title "conf-2", \
    'results/detailed_stats_optimized.dat' using ($1 + 0*offset):5:6 with boxerrorbars lc rgb "#ff7f0e" fs pattern 5 title "conf-3", \
    'results/detailed_stats_optimized2.dat' using ($1 + 1*offset):5:6 with boxerrorbars lc rgb "#2ca02c" fs pattern 3 title "conf-4", \
    'results/detailed_stats_conf-5.dat' using ($1 + 2*offset):5:6 with boxerrorbars lc rgb "#2ca02c" fs pattern 4 title "conf-5", \
    'results/detailed_stats_conf-6.dat' using ($1 + 3*offset):5:6 with boxerrorbars lc rgb "#2ca02c" fs pattern 6 title "conf-6"

# -- Inset plot -- #
set boxwidth 0.5

# Inset position
set origin 0.55,0.4
set size 0.3,0.4

unset title
unset key
unset border
unset xlabel
unset ylabel
unset y2label
unset ytics
unset y2tics

set title "Totals"

set border 4095 front lt black lw 1

set xtics ("conf-1" 1, "conf-2" 2, "conf-3" 3, "conf-4" 4, "conf-5" 5, "conf-6" 6) rotate by -25
set xrange [0.5:6.5]

stats 'results/totals_stats.dat' using 5 nooutput
set yrange [0:STATS_max * 1.1]

# Compute rounded max and mid values based on STATS_max
if (STATS_max > 1000) {
    ymax = ceil(STATS_max / 1000.0) * 1000
    ymid = ymax / 2
    set format y "%.0f"
} else if (STATS_max < 1) {
    ymax = floor(STATS_max * 1000) / 1000.0
    ymid = ymax / 2.0
    set format y "%.3f"
} else {
    ymax = ceil(STATS_max * 10) / 10.0
    ymid = ymax / 2.0
    set format y "%.1f"
}

set ytics (0, ymid, ymax)

plot \
    'results/totals_stats.dat' using 1:5:6 every ::0::0 with boxerrorbars lc rgb "#1f77b4" fs pattern 1 title "", \
    ''           using 1:5:6 every ::1::1 with boxerrorbars lc rgb "#1f77b4" fs pattern 2 title "", \
    ''           using 1:5:6 every ::2::2 with boxerrorbars lc rgb "#ff7f0e" fs pattern 5 title "", \
    ''           using 1:5:6 every ::3::3 with boxerrorbars lc rgb "#2ca02c" fs pattern 3 title "", \
    ''           using 1:5:6 every ::4::4 with boxerrorbars lc rgb "#2ca02c" fs pattern 4 title "", \
    ''           using 1:5:6 every ::5::5 with boxerrorbars lc rgb "#2ca02c" fs pattern 6 title ""

unset multiplot
