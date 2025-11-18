#!/bin/sh

metrics="Duration CO2 Energy"
units="[s] [g] [kWh]"
cols="3 4 5"

i=1
for metric in $metrics; do
    col=$(echo $cols | cut -d' ' -f$i)
    unit=$(echo $units | cut -d' ' -f$i)
    outfile="barplot_${metric}.png"

    gnuplot <<EOF
        set terminal pngcairo size 1000,600 enhanced font 'Linux Libertine Bold,12'
        set output 'results/${outfile}'

        #set style fill solid border -1
        set style fill pattern border rgb "black"

        set multiplot
        set origin 0,0
        set size 1,1
        set boxwidth 0.3
        set grid ytics

        set ylabel "${metric} ${unit}"
        set xlabel "Step"
        set xtics rotate by -10
        set key inside

        set xtics ("Trimming" 1, "Alignment" 2, "Mark Duplicates" 3, "Create FASTA Index" 4, "Create FASTA Dictionary" 5, "Base quality score" 6)
        set xrange [0:7]

        set style line 1 lc rgb "#1f77b4" lt 1  # base1
        set style line 2 lc rgb "#ff7f0e" lt 2  # base2
        set style line 3 lc rgb "#2ca02c" lt 3  # optim

        plot \
            'data/base1.dat' using (\$1 - 0.3):${col} with boxes ls 1 fs pattern 1 title "base1", \
            'data/base2.dat' using (\$1 + 0.0):${col} with boxes ls 2 fs pattern 2 title "base2", \
            'data/optimized.dat' using (\$1 + 0.3):${col} with boxes ls 3 fs pattern 5 title "optimized"

        # -- Inset plot -- #
        set datafile separator ","
        set boxwidth 0.4
        set style fill pattern border rgb "black"

        # Inset position
        set origin 0.65,0.4
        set size 0.3,0.4

        unset title
        unset xlabel
        unset ylabel
        unset key
        unset ytics
        unset border

        set title "Totals"

        set border 4095 front lt black lw 1

        set xtics ("base1" 1, "base2" 2, "optimized" 3) rotate by -25
        set xrange [0:4]

        stats 'data/totals.dat' using ${col} nooutput
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
            'data/totals.dat' using 1:${col} every ::0::0 with boxes ls 1 fs pattern 1 title "", \
            ''           using 1:${col} every ::1::1 with boxes ls 2 fs pattern 2 title "", \
            ''           using 1:${col} every ::2::2 with boxes ls 3 fs pattern 5 title ""

        unset multiplot

EOF

    echo "Generated: ${outfile}"
    i=$((i + 1))
done

