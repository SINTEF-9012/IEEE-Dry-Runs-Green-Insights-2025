#!/bin/bash

##########################################################
# Computes totals.dat for a given run.
# Usage: ./compute-totals-for-runX.sh --delete-existing=<true/false> --print-results=<true/false>
##########################################################

output_file="totals.dat"

# Check if path argument is provided
#if [ $# -eq 0 ]; then
#    echo "Usage: $0 <path_to_data_files> <run_number>" >&2
#    exit 1
#fi

# Check if second argument exists and is valid
#if [ $# -lt 2 ] || [ "$2" -lt 0 ]; then
#    echo "Invalid or missing run number: $2" >&2
#    exit 1
#fi

# Check if the delete_existing and print_results flags are set
delete_existing=true
print_results=true

for arg in "$@"; do
    case $arg in
        --delete-existing=*)
            delete_existing="${arg#*=}"
            ;;
        --print-results=*)
            print_results="${arg#*=}"
            ;;
    esac
done

echo "Delete existing: $delete_existing"
echo "Print results: $print_results"

#####################################################################



files=("base1.dat" "base2.dat" "optimized.dat" "optimized2.dat" "conf-5.dat" "conf-6.dat")
header="# [run-$2] NHRF totals - Pipeline Nr, Pipeline Name, Duration (s), CO2 (g), Energy (kWh)"
echo "$header" > "$output_file"

for j in $(seq 1 4); do
    echo -e "\nProcessing run $j..."
    data_path="./run$j/data"
    echo "Data path: $data_path"

    # Check if the data path exists
    if [[ ! -d "$data_path" ]]; then
        echo "Error: Data directory $data_path does not exist." >&2
        exit 1
    fi

    if $delete_existing; then
        rm -f "$data_path/$output_file"
    fi

    # Process each file in the data directory
    for i in "${!files[@]}"; do
        #file="${data_path}/${filename}"
        file="${data_path}/${files[$i]}"
        if [[ -f "$file" ]]; then
            # Calculate sums of columns 3, 4, and 5
            col3_sum=$(awk '{sum += $3} END {print sum}' "$file")
            col4_sum=$(awk '{sum += $4} END {print sum}' "$file")
            col5_sum=$(awk '{sum += $5} END {print sum}' "$file")
            
            # Remove file extension
            fname="${files[$i]%.dat}"

            # Append results to totals.dat
            echo "$((i+1)), \"${fname}\", $col3_sum, $col4_sum, $col5_sum" >> "$data_path/$output_file"
        else
            echo "Warning: $file not found" >&2
        fi
    done

    if $print_results; then
        printf "#-------------------------------------------------------#\n"
        cat "$data_path/$output_file"
        printf "#-------------------------------------------------------#\n"
    fi

done

#for i in "${!files[@]}"; do
#    file="${data_path}/${files[$i]}"
#    if [[ -f "$file" ]]; then
#        # Calculate sums of columns 3, 4, and 5
#        col3_sum=$(awk '{sum += $3} END {print sum}' "$file")
#        col4_sum=$(awk '{sum += $4} END {print sum}' "$file")
#        col5_sum=$(awk '{sum += $5} END {print sum}' "$file")
#        
#        # Remove file extension
#        fname="${files[$i]%.dat}"#
#
#        # Append results to totals.dat
#        echo "$((i+1)), \"${fname}\", $col3_sum, $col4_sum, $col5_sum" >> "$output_file"
#    else
#        echo "Warning: $file not found" >&2
#    fi
#done
