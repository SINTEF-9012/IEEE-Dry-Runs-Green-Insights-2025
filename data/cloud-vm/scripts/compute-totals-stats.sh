#!/bin/bash

##########################################################
# Computes averages and standard deviations for each row 
# of totals.dat files across multiple runs.
# Outputs results to totals_stats.dat
# Each row represents statistics for one pipeline across runs.
# Usage: ./compute-totals-stats.sh
# Ensure this script is run in the directory containing run*/data/
# directories with totals.dat files.
############################################################

output_file="totals_stats.dat"

# Check if run directories exist
run_dirs=(run*/data/)
if [ ${#run_dirs[@]} -eq 0 ]; then
    echo "Error: No run directories found (run*/data/)" >&2
    exit 1
fi

echo "Processing totals.dat files from runs..."

# Get all unique pipeline entries (column 2) from all totals.dat files
temp_pipelines_file=$(mktemp)
for run_dir in "${run_dirs[@]}"; do
    totals_file="${run_dir}totals.dat"
    if [[ -f "$totals_file" ]]; then
        awk '!/^#/ && NF > 0 {gsub(/[",]/, "", $2); print $2}' "$totals_file" >> "$temp_pipelines_file"
    fi
done

# Get unique pipeline names
pipeline_names=($(sort "$temp_pipelines_file" | uniq))
rm "$temp_pipelines_file"

# Create header
echo "# Totals statistics across runs - Pipeline Nr, Pipeline Name, Avg Duration (s), StdDev Duration, Avg CO2 (g), StdDev CO2, Avg Energy (kWh), StdDev Energy" > "$output_file"

# Process each unique pipeline
pipeline_counter=1
for pipeline_name in "${pipeline_names[@]}"; do
    echo "Processing pipeline: $pipeline_name"
    
    # Arrays to store values for this pipeline across all runs
    col3_values=()
    col4_values=()
    col5_values=()
    
    # Collect data for this pipeline from all runs
    for run_dir in "${run_dirs[@]}"; do
        totals_file="${run_dir}totals.dat"
        if [[ -f "$totals_file" ]]; then
            # Extract values for this specific pipeline, cleaning the pipeline name
            while IFS= read -r line; do
                if [[ -n "$line" ]]; then
                    col3_val=$(echo "$line" | awk '{print $1}')
                    col4_val=$(echo "$line" | awk '{print $2}')
                    col5_val=$(echo "$line" | awk '{print $3}')
                    
                    # Only add non-empty values
                    [[ -n "$col3_val" && "$col3_val" != "" ]] && col3_values+=("$col3_val")
                    [[ -n "$col4_val" && "$col4_val" != "" ]] && col4_values+=("$col4_val")
                    [[ -n "$col5_val" && "$col5_val" != "" ]] && col5_values+=("$col5_val")
                fi
            done < <(awk -v pipeline="$pipeline_name" '{gsub(/[",]/, "", $2); if ($2 == pipeline) print $3, $4, $5}' "$totals_file")
        fi
    done
    
    # Calculate statistics if we have data for this pipeline
    if [ ${#col3_values[@]} -gt 0 ]; then
        # Calculate averages and standard deviations
        col3_avg=$(printf '%s\n' "${col3_values[@]}" | awk '{sum+=$1} END {print sum/NR}')
        col3_std=$(printf '%s\n' "${col3_values[@]}" | awk -v avg="$col3_avg" '{sum+=($1-avg)^2} END {print sqrt(sum/NR)}')
        
        col4_avg=$(printf '%s\n' "${col4_values[@]}" | awk '{sum+=$1} END {print sum/NR}')
        col4_std=$(printf '%s\n' "${col4_values[@]}" | awk -v avg="$col4_avg" '{sum+=($1-avg)^2} END {print sqrt(sum/NR)}')
        
        col5_avg=$(printf '%s\n' "${col5_values[@]}" | awk '{sum+=$1} END {print sum/NR}')
        col5_std=$(printf '%s\n' "${col5_values[@]}" | awk -v avg="$col5_avg" '{sum+=($1-avg)^2} END {print sqrt(sum/NR)}')
        
        # Append results to the stats file with correct pipeline number and no extra commas
        echo "$pipeline_counter, \"$pipeline_name\", $col3_avg, $col3_std, $col4_avg, $col4_std, $col5_avg, $col5_std" >> "$output_file"
        
        # Increment counter for next pipeline
        ((pipeline_counter++))
    else
        echo "Warning: No data found for pipeline '$pipeline_name' across runs" >&2
    fi
done

echo "\nTotals statistics computed and saved to $output_file"
echo "Processed ${#pipeline_names[@]} pipelines across $(ls -d run*/data/ 2>/dev/null | wc -l) runs"
