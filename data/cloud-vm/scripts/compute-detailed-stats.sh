#!/bin/bash

##########################################################
# Computes detailed step-by-step averages and standard
# deviations across multiple runs.
# Outputs results to files named detailed_stats_<step_name>.dat
# where <step_name> is the name of the step.
# Each file contains the average and standard deviation for
# duration, CO2 emissions, and energy consumption for each step.
# Usage: ./compute-detailed-stats.sh
# Ensure this script is run in the directory containing run*/data/
# directories with the relevant .dat files.
############################################################

output_prefix="detailed_stats"
files=("base1.dat" "base2.dat" "optimized.dat" "optimized2.dat" "conf-5.dat" "conf-6.dat")


# Check if run directories exist
run_dirs=(run*/data/)
if [ ${#run_dirs[@]} -eq 0 ]; then
    echo "Error: No run directories found (run*/data/)" >&2
    exit 1
fi

for filename in "${files[@]}"; do
    fname="${filename%.dat}"
    output_file="${output_prefix}_${fname}.dat"

    echo "Processing $filename..."

    # Get all unique step names from column 2 across all runs, removing quotes and commas
    temp_steps_file=$(mktemp)
    for run_dir in "${run_dirs[@]}"; do
        file="${run_dir}${filename}"
        if [[ -f "$file" ]]; then
            awk '!/^#/ && NF > 0 {gsub(/[",]/, "", $2); print $2}' "$file" >> "$temp_steps_file"
        fi
    done

    # Get unique step names
    all_step_names=($(sort "$temp_steps_file" | uniq))
    rm "$temp_steps_file"

    # Define the desired step order
    ordered_steps=("trimming" "alignment" "mark-duplicates" "create-fasta-index" "create-fasta-dict" "base-quality-score")

    # Create header for this file
    echo "# Detailed statistics for $fname - Step Name, Avg Duration (s), StdDev Duration, Avg CO2 (g), StdDev CO2, Avg Energy (kWh), StdDev Energy" > "$output_file"

    # Process each step in the desired order
    for step_nr in "${!ordered_steps[@]}"; do
        step_name="${ordered_steps[$step_nr]}"
        # Check if this step exists in the data
        if [[ ! " ${all_step_names[@]} " =~ " ${step_name} " ]]; then
            echo "Warning: Step '$step_name' not found in data for $filename" >&2
            continue
        fi

        # Arrays to store values for this step across all runs
        step_number=$((step_nr + 1))
        col3_values=()
        col4_values=()
        col5_values=()

        # Collect data for this step from all runs
        for run_dir in "${run_dirs[@]}"; do
            file="${run_dir}${filename}"
            if [[ -f "$file" ]]; then
                # Extract values for this specific step, matching by cleaned step name
                while IFS= read -r line; do
                    if [[ -n "$line" ]]; then
                        col3_val=$(echo "$line" | awk '{print $1}')
                        col4_val=$(echo "$line" | awk '{print $2}')
                        col5_val=$(echo "$line" | awk '{print $3}')

                        # Only add non-empty values
                        [[ -n "$col3_val" ]] && col3_values+=("$col3_val")
                        [[ -n "$col4_val" ]] && col4_values+=("$col4_val")
                        [[ -n "$col5_val" ]] && col5_values+=("$col5_val")
                    fi
                done < <(awk -v step="$step_name" '{gsub(/[",]/, "", $2); if ($2 == step) print $3, $4, $5}' "$file")
            fi
        done

        # Calculate statistics if we have data for this step
        if [ ${#col3_values[@]} -gt 0 ]; then
            # Calculate averages and standard deviations
            col3_avg=$(printf '%s\n' "${col3_values[@]}" | awk '{sum+=$1} END {print sum/NR}')
            col3_std=$(printf '%s\n' "${col3_values[@]}" | awk -v avg="$col3_avg" '{sum+=($1-avg)^2} END {print sqrt(sum/NR)}')

            col4_avg=$(printf '%s\n' "${col4_values[@]}" | awk '{sum+=$1} END {print sum/NR}')
            col4_std=$(printf '%s\n' "${col4_values[@]}" | awk -v avg="$col4_avg" '{sum+=($1-avg)^2} END {print sqrt(sum/NR)}')

            col5_avg=$(printf '%s\n' "${col5_values[@]}" | awk '{sum+=$1} END {print sum/NR}')
            col5_std=$(printf '%s\n' "${col5_values[@]}" | awk -v avg="$col5_avg" '{sum+=($1-avg)^2} END {print sqrt(sum/NR)}')

            # Append results to the detailed stats file
            echo "${step_number}, \"${step_name}\", $col3_avg, $col3_std, $col4_avg, $col4_std, $col5_avg, $col5_std" >> "$output_file"
        else
            echo "Warning: No data found for step '$step_name' in $filename" >&2
        fi
    done

    echo "Detailed statistics for $fname saved to $output_file"
done

echo "All detailed statistics computed!"
