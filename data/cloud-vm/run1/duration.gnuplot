set terminal pngcairo size 1000,600 enhanced font 'Linux Libertine Bold,10'
set output 'duration.png'

set multiplot
set style fill pattern border rgb "black"

set origin 0,0
set size 1,1
set boxwidth 0.3
set grid ytics

set title "NHRF Pipeline Metrics by Step - ${metric} ${unit}"
set ylabel "${metric} ${unit}"
set xlabel "Step"
set xtics rotate by -15
set key inside

set xtics ("Trimming" 1, "Alignment" 2, "Mark duplicates" 3, "Create FASTA index" 4, "Base quality score" 5)
set xrange [0:6]

set style line 1 lc rgb "#1f77b4" lt 1  # base1
set style line 2 lc rgb "#ff7f0e" lt 2  # base2
set style line 3 lc rgb "#2ca02c" lt 3  # optim
set style line 4 lc rgb "#2ca02d" lt 3  # optim2


plot \
    'nhrf-base1.dat' using ($1 - 0.3):3 with boxes ls 1 fs pattern 1 title "base1", \
    'nhrf-base2.dat' using ($1 + 0.0):3 with boxes ls 2 fs pattern 2 title "base2", \
    'nhrf-optimized.dat' using ($1 + 0.3):3 with boxes ls 3 fs pattern 5 title "optimized", \
    'nhrf-optimized2.dat' using ($1 + 0.5):3 with boxes ls 4 fs pattern 5 title "optimized2"

# -- Inset plot -- #
set datafile separator ","
set boxwidth 0.4
set style fill pattern border rgb "black"

# Inset position
set origin 0.65,0.4
set size 0.3,0.3

unset title
unset xlabel
unset ylabel
unset key
unset ytics
unset border

set title "Totals"

set border 4095 front lt black lw 1

set xtics ("base1" 1, "base2" 2, "optimized" 3)
set xrange [0:4]

stats 'totals.dat' using 3 nooutput
set yrange [0:STATS_max * 1.1]
set ytics auto

# Choose column depending on metric (assumes you predefine col)
#plot \
#    'totals.dat' using 1:3 with boxes ls 1 fs pattern 1 title "", \
#    '' using 1:4 with boxes ls 2 fs pattern 2 title "", \
#    '' using 1:5 with boxes ls 3 fs pattern 5 title ""


plot \
    'totals.dat' using 1:3 every ::0::0 with boxes ls 1 fs pattern 1 title "", \
    '' using 1:3 every ::1::1 with boxes ls 2 fs pattern 2 title "", \
    '' using 1:3 every ::2::2 with boxes ls 3 fs pattern 5 title ""

unset multiplot
