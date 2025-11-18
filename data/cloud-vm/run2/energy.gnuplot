# NHRF data pipeline - plot Energy barplot
##############################################################################

set terminal pngcairo size 1000,600 enhanced font 'Linux Libertine Bold,12'
set output 'results/energy.png'

set datafile separator ","

set style fill pattern border rgb "black"

set multiplot
set origin 0,0
set size 1,1
set boxwidth 0.2
set grid ytics

set ylabel "Energy [kWh]"
set xlabel "Step"
set xtics rotate by -10
set key inside

set xtics ("Trimming" 1, "Alignment" 2, "Mark Duplicates" 3, "Create FASTA Index" 4, "Create FASTA Dictionary" 5, "Base quality score" 6)
set xrange [0.5:7]
#set yrange [0:10000]

plot \
    'data/base1.dat' using ($1 - 0.2):5 with boxes lc rgb "#1f77b4" fs pattern 1 title "conf-1", \
    'data/base2.dat' using ($1 - 0.0):5 with boxes lc rgb "#1f77b4" fs pattern 2 title "conf-2", \
    'data/optimized.dat' using ($1 + 0.2):5 with boxes lc rgb "#ff7f0e" fs pattern 5 title "combined (conf-1 and conf-2)", \
    'data/optimized2.dat' using ($1 + 0.4):5 with boxes lc rgb "#2ca02c" fs pattern 3 title "conf-4"

# -- Inset plot -- #
set boxwidth 0.4

# Inset position
set origin 0.6,0.4
set size 0.3,0.4

unset title
unset xlabel
unset ylabel
unset key
unset ytics
unset border

set title "Totals"

set border 4095 front lt black lw 1

set xtics ("conf-1" 1, "conf-2" 2, "combined" 3, "conf-4" 4) rotate by -25
set xrange [0:5]

stats 'data/totals.dat' using 5 nooutput
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
    'data/totals.dat' using 1:5 every ::0::0 with boxes lc rgb "#1f77b4" fs pattern 1 title "", \
    ''           using 1:5 every ::1::1 with boxes lc rgb "#1f77b4" fs pattern 2 title "", \
    ''           using 1:5 every ::2::2 with boxes lc rgb "#ff7f0e" fs pattern 5 title "", \
    ''           using 1:5 every ::3::3 with boxes lc rgb "#2ca02c" fs pattern 3 title ""

unset multiplot
