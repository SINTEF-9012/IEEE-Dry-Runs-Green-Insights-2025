### Energy Statistics and plotting
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def get_power_data(data_path: str = "./data_tapo-p115-sct-sd/Power.xls") -> pd.DataFrame:
    raw_power_data = pd.read_excel(data_path)
    raw_power_data = raw_power_data.rename(columns={raw_power_data.columns[0]: 'Date'})
    raw_power_data[raw_power_data.columns[0]] = pd.to_datetime(raw_power_data[raw_power_data.columns[0]])
    # Convert to numeric and drop rows that can't be converted
    raw_power_data = raw_power_data[pd.to_numeric(raw_power_data['Power(W)'], errors='coerce').notna()]
    raw_power_data['Power(W)'] = pd.to_numeric(raw_power_data['Power(W)'])
    raw_power_data["Energy(kWh)"] = raw_power_data['Power(W)'] / 1000 * (raw_power_data['Date'].diff().dt.total_seconds() / 3600)
    #raw_power_data.columns
    raw_power_data = raw_power_data[pd.to_numeric(raw_power_data['Energy(kWh)'], errors='coerce').notna()]
    raw_power_data['Energy(kWh)'] = pd.to_numeric(raw_power_data['Energy(kWh)'])
    return raw_power_data


def get_time_periods(
        df: pd.DataFrame,
        start_date_baseline: str = None,
        end_date_baseline: str = None,
        dt_format: str = '%Y-%m-%d %H:%M:%S') -> list:
    """
    Get the time period of interest from the DataFrame.
    
    Parameters:
        df (pd.DataFrame): DataFrame with a 'Date' column
        time_shift (float): Time shift in minutes to apply to the 'Date' column
        start_date_baseline (str or pd.Timestamp): Start timestamp for baseline
        end_date_baseline (str or pd.Timestamp): End timestamp for baseline
    
    Returns:
        list of tuples: Each tuple contains (step_name, start_time, stop_time)
        The baseline step is an additional reference point to establish a baseline for power and energy consumption
    """

    time_periods_ct = []
    if (start_date_baseline is not None) and (end_date_baseline is not None):
        print("    get_time_periods -- start and end times present. Assuming baseline period.")
        print("     appending baseline period")
        time_periods_ct.append(('baseline', start_date_baseline, end_date_baseline))
    else:
        print("    get_time_periods -- start and end times NOT present. NO baseline step appended.")
    for _, row in df.iterrows():
        step_name = row['step']
        start_time = pd.to_datetime(row['start']).strftime(dt_format)
        stop_time = pd.to_datetime(row['stop']).strftime(dt_format)
        time_periods_ct.append((step_name, start_time, stop_time))
    print("    get_time_periods -- extracted time periods:")
    for period in time_periods_ct:
        print(f"      - {period[0]}: {period[1]} to {period[2]}")
    return time_periods_ct


def divide_power_data_into_step_periods(time_periods: list, power_dataframe: pd.DataFrame) -> list:
    """
    Divide the power data into segments based on the specified time periods.


    """
    print()
    print("     divide_power_data_into_step_periods...")
    data_periods = []
    n_time_periods = len(time_periods)
    baseline_energy = 0
    baseline_power = 0
    counter = 0
    for name, start, end in time_periods:
        counter += 1
        print(f"        Processing {name}...")
        print(f"            start: {start}, end: {end}")
        stats = compute_energy_stats(power_dataframe, start, end)
        if stats['filtered_data'].empty or stats['filtered_data'] is None: 
            print(f"        Warning! No data for period: {name}")
            #print("    Warning! Adding empty data!")
            #data_periods.append({"Date": [], "Energy(kWh)": [], "Power(W)": []})

        if name == "baseline":
            print("        Setting baseline energy and power values from baseline step.")
            baseline_energy = stats['filtered_data']['Energy(kWh)'].mean()
            baseline_power = stats['filtered_data']['Power(W)'].mean()


        if n_time_periods == counter:
            print("        Last segment detected.")
            # if last segment, compute fraction of step after to add to segment
            # if segment contains no data (filtered_data is empty), use next step as datapoint and divide by fraction of start-stop
            if isinstance(stats['filtered_data'], pd.DataFrame) and not stats['filtered_data'].empty:
                print("        Last segment contains data.")
                t1 = stats['filtered_data']['Date'].max() # last timestamp of segment
                t2 = power_dataframe[power_dataframe['Date'] > t1]['Date'].min() # first timestamp after segment
                end_timestamp = pd.to_datetime(end) # end time of segment (according to carbontracker input)
                d1 = end_timestamp - t1 # time between t1 and end time
                d2 = t2 - end_timestamp # time between end time and t2
                fraction = d2 / (d1 + d2) # fraction of step after last data point that contributes to last step in the segment
                # set the last timestamp of segment equal to the end_timestamp
                stats['filtered_data'].loc[stats['filtered_data']['Date'].idxmax(), 'Date'] = end_timestamp
                # adjust the energy value of the last segment datapoint accordingly
                stats['filtered_data'].loc[stats['filtered_data']['Date'].idxmax(), 'Energy(kWh)'] *= fraction
                # val = stats['filtered_data'].loc[stats['filtered_data']['Date'].idxmax(), 'Power(W)']
                # print(f" val: {val}, dtype: {type(val)}") # it is ok, the value type is numpy.int64
                stats['filtered_data'].loc[stats['filtered_data']['Date'].idxmax(), 'Power(W)'] *= fraction
            else:
                # last segment does not contain any data. Use next timestep as datapoint, and devide by fraction of start-stop
                print("        Last segment contains NO data.")
                start = pd.to_datetime(start)
                stop = pd.to_datetime(end)
                dt = stop - start
                t1 = power_dataframe[power_dataframe['Date'] < start]['Date'].max() # first timestamp before segment
                t2 = power_dataframe[power_dataframe['Date'] > stop]['Date'].min() # first timestamp after segment
                fraction = dt / (t2 - t1) # fraction of step that contributes to last step in the segment
                p2 = power_dataframe[power_dataframe['Date'] == t2]['Power(W)'].values[0] if not power_dataframe[power_dataframe['Date'] == t2].empty else 0
                e2 = power_dataframe[power_dataframe['Date'] == t2]['Energy(kWh)'].values[0] if not power_dataframe[power_dataframe['Date'] == t2].empty else 0
                print(f"        Using datapoint at {t2} with Power={p2}W, Energy={e2}kWh, fraction={fraction}, baseline_energy={baseline_energy}, baseline_power={baseline_power}")
                stats['filtered_data'] = pd.DataFrame({
                    'Date': [stop],
                    'Energy(kWh)': [(e2 - baseline_energy) * fraction + baseline_energy],
                    'Power(W)': [(p2 - baseline_power) * fraction + baseline_power]
                })
        data_periods.append(stats['filtered_data'])

    return data_periods


def compute_energy_stats(
        df: pd.DataFrame,
        start_date: str,
        end_date: str) -> dict:
    """
    Compute energy statistics between two timestamps.
    
    Parameters:
    df (pd.DataFrame): DataFrame with 'Date' and 'Energy(kWh)' columns
    start_date (str or pd.Timestamp): Start timestamp
    end_date (str or pd.Timestamp): End timestamp
    
    Returns:
    dict: Dictionary with energy statistics
    """
    # Convert string dates to datetime if needed
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filter data between the two timestamps
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    filtered_data = df.loc[mask]
    
    if filtered_data.empty:
        print(f"No data found between {start_date} and {end_date}")
        return {'total_energy': 0, 'avg_power': 0, 'max_power': 0, 'min_power': 0, 'filtered_data': pd.DataFrame()}
    
    # Calculate statistics
    total_energy = filtered_data['Energy(kWh)'].sum()
    avg_power = filtered_data['Power(W)'].mean()
    max_power = filtered_data['Power(W)'].max()
    min_power = filtered_data['Power(W)'].min()
    
    return {
        'total_energy': total_energy,
        'avg_power': avg_power,
        'max_power': max_power,
        'min_power': min_power,
        'filtered_data': filtered_data
    }


def compute_baseline_stats(
        df: pd.DataFrame,
        percentile_threshold: float = 70.0,
        print_stats: bool = True):
    # Step 1: Baseline Power Consumption Analysis
    """
    Analyze baseline power consumption by identifying periods with stable, low power usage.

    Parameters:
    df: DataFrame with Date, Power(W), Energy(kWh) columns
    percentile_threshold: Percentile below which we consider power as "baseline"

    Returns:
    dict with baseline statistics
    """
    # Calculate power threshold for baseline (e.g., 75th percentile and below)
    power_threshold = np.percentile(df['Power(W)'], percentile_threshold)

    # Identify baseline periods
    baseline_mask = df['Power(W)'] <= power_threshold
    baseline_data = df[baseline_mask].copy()

    # Calculate baseline statistics
    baseline_stats = {
        'threshold_power': power_threshold,
        'baseline_periods': len(baseline_data),
        'total_periods': len(df),
        'baseline_percentage': len(baseline_data) / len(df) * 100,
        'mean_power': baseline_data['Power(W)'].mean(),
        'median_power': baseline_data['Power(W)'].median(),
        'std_power': baseline_data['Power(W)'].std(),
        'min_power': baseline_data['Power(W)'].min(),
        'max_power': baseline_data['Power(W)'].max(),
        'mean_energy': baseline_data['Energy(kWh)'].mean(),
        'total_baseline_energy': baseline_data['Energy(kWh)'].sum()
    }

    if print_stats:
        print("     compute_baseline_stats -- Baseline analysis...")
        print(f"      Power threshold for baseline: {baseline_stats['threshold_power']:.1f} W")
        print(f"      Baseline periods: {baseline_stats['baseline_periods']} out of {baseline_stats['total_periods']} ({baseline_stats['baseline_percentage']:.1f}%)")
        print(f"      Mean baseline power: {baseline_stats['mean_power']:.1f} W")
        print(f"      Median baseline power: {baseline_stats['median_power']:.1f} W")
        print(f"      Std baseline power: {baseline_stats['std_power']:.1f} W")
        print(f"      Power range: {baseline_stats['min_power']:.1f} - {baseline_stats['max_power']:.1f} W")
        print(f"      Mean baseline energy per period: {baseline_stats['mean_energy']:.6f} kWh")
        print(f"      Total baseline energy: {baseline_stats['total_baseline_energy']:.4f} kWh")
        print()

    return baseline_stats


# Step 2: Power Surge Detection

def detect_power_surges(
        df: pd.DataFrame,
        baseline_stats: dict,
        surge_threshold_multiplier=1.2,
        min_duration_minutes=10):
    """
    Detect periods of increased power usage (surges).

    Parameters:
    df: DataFrame with Date, Power(W), Energy(kWh) columns
    baseline_stats: Dictionary with baseline statistics
    surge_threshold_multiplier: Multiplier above baseline mean to consider as surge
    min_duration_minutes: Minimum duration in minutes to consider as a valid surge period

    Returns:
    List of surge periods with start/end times and statistics
    """
    # Define surge threshold
    surge_threshold = baseline_stats['mean_power'] * surge_threshold_multiplier

    # Identify surge points
    df_copy = df.copy()
    df_copy['is_surge'] = df_copy['Power(W)'] > surge_threshold

    # Find continuous surge periods
    surge_periods = []
    in_surge = False
    surge_start = None
    surge_data = []

    for idx, row in df_copy.iterrows():
        if row['is_surge'] and not in_surge:
            # Start of new surge
            in_surge = True
            surge_start = row['Date']
            surge_data = [row]
        elif row['is_surge'] and in_surge:
            # Continue surge
            surge_data.append(row)
        elif not row['is_surge'] and in_surge:
            # End of surge
            surge_end = surge_data[-1]['Date']
            surge_duration = (surge_end - surge_start).total_seconds() / 60  # minutes

            # Only keep surges longer than minimum duration
            if surge_duration >= min_duration_minutes:
                surge_df = pd.DataFrame(surge_data)
                surge_info = {
                    'start_time': surge_start,
                    'end_time': surge_end,
                    'duration_minutes': surge_duration,
                    'peak_power': surge_df['Power(W)'].max(),
                    'avg_power': surge_df['Power(W)'].mean(),
                    'min_power': surge_df['Power(W)'].min(),
                    'total_energy': surge_df['Energy(kWh)'].sum(),
                    'data_points': len(surge_df),
                    'avg_energy_per_point': surge_df['Energy(kWh)'].mean(),
                    'surge_data': surge_df
                }
                # Calculate energy above baseline
                baseline_energy_equivalent = len(surge_df) * baseline_stats['mean_energy']
                surge_info['energy_above_baseline'] = surge_info['total_energy'] - baseline_energy_equivalent

                surge_periods.append(surge_info)

            # Reset for next potential surge
            in_surge = False
            surge_data = []

    return surge_periods, surge_threshold


def compute_surge_vs_simpipe_start_endtime_diffs(
        carbontracker_simpipe_data: pd.DataFrame,
        surge_periods: list):
    # Step 6: Time Difference Analysis between Power Surges and Carbontracker

    first_start_dt = pd.to_datetime(carbontracker_simpipe_data['start'].iloc[0]).tz_localize(None)
    last_stop_dt = pd.to_datetime(carbontracker_simpipe_data['stop'].iloc[-1]).tz_localize(None)

    print("=== TIME DIFFERENCE ANALYSIS ===")
    print(f"Carbontracker start time: {first_start_dt}")
    print(f"Carbontracker stop time: {last_stop_dt}")
    print(f"Carbontracker duration: {(last_stop_dt - first_start_dt).total_seconds() / 60:.1f} minutes\n")

    # Calculate differences for each surge
    for i, surge in enumerate(surge_periods, 1):
        surge_start = surge['start_time']
        surge_end = surge['end_time']

        # Time differences in seconds (positive = surge comes after carbontracker)
        start_diff_seconds = (surge_start - first_start_dt).total_seconds()
        end_diff_seconds = (surge_end - last_stop_dt).total_seconds()

        # Convert to hours and minutes for readability
        start_diff_hours = start_diff_seconds / 3600
        end_diff_hours = end_diff_seconds / 3600

        print(f"Surge {i}:")
        print(f"  Surge start: {surge_start}")
        print(f"  Surge end: {surge_end}")
        print("  Start time difference from carbontracker start:")
        if start_diff_seconds >= 0:
            print(f"    +{abs(start_diff_hours):.2f} hours ({abs(start_diff_seconds/60):.1f} minutes) AFTER carbontracker start")
        else:
            print(f"    -{abs(start_diff_hours):.2f} hours ({abs(start_diff_seconds/60):.1f} minutes) BEFORE carbontracker start")

        print("  End time difference from carbontracker stop:")
        if end_diff_seconds >= 0:
            print(f"    +{abs(end_diff_hours):.2f} hours ({abs(end_diff_seconds/60):.1f} minutes) AFTER carbontracker stop")
        else:
            print(f"    -{abs(end_diff_hours):.2f} hours ({abs(end_diff_seconds/60):.1f} minutes) BEFORE carbontracker stop")
        print()

    # Summary of timing relationships
    print("=== TIMING RELATIONSHIPS SUMMARY ===")
    surges_before_ct = sum(1 for surge in surge_periods if surge['start_time'] < first_start_dt)
    surges_during_ct = sum(1 for surge in surge_periods
                        if surge['start_time'] <= last_stop_dt and surge['end_time'] >= first_start_dt)
    surges_after_ct = sum(1 for surge in surge_periods if surge['start_time'] > last_stop_dt)

    print(f"Surges starting before carbontracker         : {surges_before_ct}")
    print(f"Surges overlapping with carbontracker period : {surges_during_ct}")
    print(f"Surges starting after carbontracker          : {surges_after_ct}")

    # Check which surge is closest to carbontracker start
    closest_start_surge = None
    min_start_diff = float('inf')

    for i, surge in enumerate(surge_periods, 1):
        start_diff = abs((surge['start_time'] - first_start_dt).total_seconds())
        if start_diff < min_start_diff:
            min_start_diff = start_diff
            closest_start_surge = i

    if closest_start_surge:
        closest_surge = surge_periods[closest_start_surge - 1]
        diff_minutes = min_start_diff / 60
        print(f"\nClosest surge to carbontracker start      : Surge {closest_start_surge}")
        print(f"Time difference: {diff_minutes:.1f} minutes")

        # Check if this surge overlaps with carbontracker execution
        if (closest_surge['start_time'] <= last_stop_dt and
            closest_surge['end_time'] >= first_start_dt):
            print("This surge OVERLAPS with carbontracker execution period")
        else:
            print("This surge does NOT overlap with carbontracker execution period")    


def compute_relative_energy_usage(
        power_data_segments: pd.DataFrame, 
        time_periods: list,
        baseline_stats: dict = None) -> (pd.DataFrame, float, float, float):
    """
    Compute the relative energy usage for each segment.

    Parameters:
    power_data_segments (list): List of power data segments

    Returns:
    pd.DataFrame: DataFrame with relative energy usage
    """

    # Total relative energy usage (relative to baseline)
    total_relative_energy = 0
    baseline_energy = 0
    # Total absolute energy usage (without baseline subtraction)
    total_absolute_energy = 0

    baseline_segment = power_data_segments[0]  # assume that this corresponds to the baseline
    try:
        baseline_energy = baseline_segment['Energy(kWh)'].mean()
    except KeyError:
        print("    Warning! Could not compute baseline energy:")
        print(baseline_energy)

    if baseline_stats is not None:
        print(f"    Using baseline energy from baseline_stats: {baseline_stats['mean_energy']} kWh")
        print(f"    Baseline energy from baseline_segment    : {baseline_energy} kWh")
        baseline_energy = baseline_stats['mean_energy']
    outdf = pd.DataFrame(columns=["step", "start", "stop", "duration", "energy(kWh)"])

    segment_nr = 1
    start_segment = 1
    for segment in power_data_segments[start_segment:]:
        print(f"    Processing segment {segment_nr}")
        if not segment.empty:
            total_energy = segment['Energy(kWh)'].sum()
            relative_energy = segment['Energy(kWh)'] - baseline_energy
            segment_energy = relative_energy.sum()
            total_absolute_energy += total_energy
            total_relative_energy += segment_energy
            step = time_periods[segment_nr][0]
            print(f"    Step: {step}")
            start = time_periods[segment_nr][1]
            stop = time_periods[segment_nr][2]
            duration = (pd.to_datetime(stop) - pd.to_datetime(start)).total_seconds()
            new_row = pd.DataFrame([{"step": step, "start": start, "stop": stop, "duration": duration, "energy(kWh)": segment_energy, "absolute_energy(kWh)": total_energy}])
            outdf = pd.concat([outdf, new_row], ignore_index=True)
        else:
            print(f"    Warning! Empty segment {segment_nr}")
        # increment the segment_nr
        segment_nr += 1
    print(f"Total absolute energy consumption (kWh): {total_absolute_energy}")
    print(f"Total relative energy consumption (kWh): {total_relative_energy}")
    return outdf, baseline_energy, total_absolute_energy, total_relative_energy


### Plotting


def plot_energy_usage(
        df: pd.DataFrame,
        x_col: str = 'Date',
        y_col: str = 'Energy(kWh)',
        title: str = 'Energy Usage Over Time',
        start: str = None,
        end: str = None,
        timestamps: str = None):
    """
    Plot energy usage over time using matplotlib.pyplot
    
    Parameters:
    df (pd.DataFrame): DataFrame with date and energy columns
    x_col (str): Column name for x-axis (default: 'Date')
    y_col (str): Column name for y-axis (default: 'Energy(kWh)')
    title (str): Plot title
    start (str): Start timestamp for filtering data
    end (str): End timestamp for filtering data
    timestamps (list): Optional list of timestamps for highlighting specific events
        * plot vertical line(s) at given timestamps
    """
    
    if start and end:
        copy = df[(df[x_col] >= start) & (df[x_col] <= end)]
    elif start:
        copy = df[df[x_col] >= start]
    elif end:
        copy = df[df[x_col] <= end]
    else:
        copy = df

    plt.figure(figsize=(10, 6))
    plt.plot(copy[x_col], copy[y_col])
    
    # Add vertical lines at specified timestamps
    if timestamps is not None:
        for timestamp in timestamps:
            plt.axvline(x=pd.to_datetime(timestamp), color='red', linestyle='--', alpha=0.7, label='Event')

    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_energy_usage_overlay_multiple_datasets(
        raw_power_data: pd.DataFrame, 
        data_periods: pd.DataFrame, 
        time_periods_ct: list, 
        start_time: str = None, 
        end_time: str = None) -> None:
    """
    This plots the data as specified in plot_energy_usage and on top plots the multiple datasets as plot_multiple_datasets().
    """
    # Filter the raw data for the specified time range
    if start_time and end_time:
        filtered_raw = raw_power_data[(raw_power_data['Date'] >= start_time) & (raw_power_data['Date'] <= end_time)]
    elif start_time:
        filtered_raw = raw_power_data[raw_power_data['Date'] >= start_time]
    elif end_time:
        filtered_raw = raw_power_data[raw_power_data['Date'] <= end_time]
    else:
        filtered_raw = raw_power_data

    # Create single plot with both datasets
    plt.figure(figsize=(12, 6))
    
    # Plot the overall energy usage first (as background)
    plt.plot(filtered_raw['Date'], filtered_raw['Energy(kWh)'], 
             color='lightgray', alpha=0.7, linewidth=2, label='Overall Energy Usage')
    
    # Overlay the multiple datasets on the same plot
    for i, df in enumerate(data_periods):
        if not isinstance(df, pd.DataFrame):
            print(f"Dataset {i} is not a valid DataFrame.")
            continue
        # Use provided label or generate default
        if i < len(time_periods_ct):
            label = time_periods_ct[i][0]
        else:
            # Create label from date range
            start_date = df['Date'].min().strftime('%Y-%m-%d %H:%M')
            end_date = df['Date'].max().strftime('%Y-%m-%d %H:%M')
            label = f"Dataset {i+1}: {start_date} to {end_date}"
        
        plt.plot(df['Date'], df['Energy(kWh)'], label=label, marker='o', markersize=3)
    
    plt.xlabel('Date')
    plt.ylabel('Energy(kWh)')
    plt.title('Energy Usage Over Time with Multiple Datasets Overlay')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_multiple_datasets(datasets_list, time_periods, column='Power(W)', title=None):
    """
    Plot multiple filtered datasets as separate lines.
    
    Parameters:
    datasets_list (list): List of DataFrames (filtered_data from compute_energy_stats)
    labels (list): Optional list of labels for each dataset
    column (str): Column to plot ('Power(W)' or 'Energy(kWh)')
    title (str): Optional plot title
    """
    plt.figure(figsize=(12, 6))
    
    for i, df in enumerate(datasets_list):
        if df.empty:
            continue
            
        # Use provided label or generate default
        if time_periods and i < len(time_periods):
            label = time_periods[i][0]
        else:
            # Create label from date range
            start_date = df['Date'].min().strftime('%Y-%m-%d %H:%M')
            end_date = df['Date'].max().strftime('%Y-%m-%d %H:%M')
            label = f"Dataset {i+1}: {start_date} to {end_date}"
        
        plt.plot(df['Date'], df[column], label=label, marker='o', markersize=3)
    
    plt.xlabel('Date')
    plt.ylabel(column)
    plt.title(title or f'{column} Over Time - Multiple Datasets')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_enhanced_visualization(
        carbontracker_simpipe_data: pd.DataFrame,
        power_data: pd.DataFrame,
        baseline_stats: dict,
        surge_periods: list,
        surge_threshold: float):
    # Step 5: Enhanced Visualization with Surge Periods and Carbontracker Markers

    # Convert carbontracker timestamps to datetime and make timezone-naive for comparison
    first_start_dt = pd.to_datetime(carbontracker_simpipe_data['start'].iloc[0]).tz_localize(None)
    last_stop_dt = pd.to_datetime(carbontracker_simpipe_data['stop'].iloc[-1]).tz_localize(None)

    print(f"Carbontracker period: {first_start_dt} to {last_stop_dt}")
    print(f"Power data period: {power_data['Date'].min()} to {power_data['Date'].max()}")

    # Create the enhanced plot
    plt.figure(figsize=(16, 10))

    # Main power consumption plot
    plt.subplot(2, 1, 1)
    plt.plot(power_data['Date'], power_data['Power(W)'], linewidth=1, alpha=0.7, color='blue', label='Power Consumption')

    # Add baseline threshold line
    plt.axhline(y=baseline_stats['mean_power'], color='green', linestyle='--',
            label=f'Baseline Mean ({baseline_stats["mean_power"]:.1f} W)')
    plt.axhline(y=surge_threshold, color='red', linestyle='--',
            label=f'Surge Threshold ({surge_threshold:.1f} W)')

    # Highlight surge periods
    for i, surge in enumerate(surge_periods):
        plt.axvspan(surge['start_time'], surge['end_time'],
                alpha=0.3, color='red', label=f'Surge {i+1}' if i == 0 else "")

    # Add carbontracker start and stop markers
    plt.axvline(x=first_start_dt, color='purple', linestyle='-', linewidth=2, alpha=0.8,
            label=f'Carbontracker Start ({first_start_dt.strftime("%H:%M")})')
    plt.axvline(x=last_stop_dt, color='purple', linestyle='-', linewidth=2, alpha=0.8,
            label=f'Carbontracker End ({last_stop_dt.strftime("%H:%M")})')

    plt.title('Power Consumption with Surge Periods and Carbontracker Timeline')
    plt.ylabel('Power (W)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)

    # Energy consumption plot
    plt.subplot(2, 1, 2)
    plt.plot(power_data['Date'], power_data['Energy(kWh)'], linewidth=1, alpha=0.7, color='orange', label='Energy Consumption')

    # Add baseline energy line
    plt.axhline(y=baseline_stats['mean_energy'], color='green', linestyle='--',
            label=f'Baseline Mean ({baseline_stats["mean_energy"]:.6f} kWh)')

    # Highlight surge periods
    for i, surge in enumerate(surge_periods):
        plt.axvspan(surge['start_time'], surge['end_time'],
                alpha=0.3, color='red')

    # Add carbontracker start and stop markers
    plt.axvline(x=first_start_dt, color='purple', linestyle='-', linewidth=2, alpha=0.8)
    plt.axvline(x=last_stop_dt, color='purple', linestyle='-', linewidth=2, alpha=0.8)

    plt.title('Energy Consumption with Surge Periods and Carbontracker Timeline')
    plt.ylabel('Energy (kWh)')
    plt.xlabel('Date')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

    # Analysis of carbontracker period vs power surges
    print("=== CARBONTRACKER vs POWER SURGE ANALYSIS ===")
    print(f"Carbontracker monitoring period: {first_start_dt.strftime('%H:%M')} - {last_stop_dt.strftime('%H:%M')}")
    carbontracker_duration = (last_stop_dt - first_start_dt).total_seconds() / 3600
    print(f"Carbontracker duration: {carbontracker_duration:.2f} hours")

    # Check overlap with surge periods
    print("\nOverlap analysis with detected surge periods:")
    for i, surge in enumerate(surge_periods, 1):
        surge_start = surge['start_time']
        surge_end = surge['end_time']

        # Check if there's overlap
        overlap_start = max(first_start_dt, surge_start)
        overlap_end = min(last_stop_dt, surge_end)

        if overlap_start < overlap_end:
            overlap_duration = (overlap_end - overlap_start).total_seconds() / 60
            surge_duration = surge['duration_minutes']
            overlap_percentage = (overlap_duration / surge_duration) * 100
            print(f"  Surge {i}: {overlap_percentage:.1f}% overlap ({overlap_duration:.1f}/{surge_duration:.1f} minutes)")
            print(f"    Surge: {surge_start.strftime('%H:%M')} - {surge_end.strftime('%H:%M')}")
            print(f"    Overlap: {overlap_start.strftime('%H:%M')} - {overlap_end.strftime('%H:%M')}")
        else:
            print(f"  Surge {i}: No overlap")
            print(f"    Surge: {surge_start.strftime('%H:%M')} - {surge_end.strftime('%H:%M')}")

    # Calculate energy during carbontracker period
    ct_mask = (power_data['Date'] >= first_start_dt) & (power_data['Date'] <= last_stop_dt)
    ct_power_data = power_data[ct_mask]

    if len(ct_power_data) > 0:
        ct_total_energy = ct_power_data['Energy(kWh)'].sum()
        ct_avg_power = ct_power_data['Power(W)'].mean()
        ct_peak_power = ct_power_data['Power(W)'].max()

        print("\nPower statistics during Carbontracker period:")
        print(f"  Average power: {ct_avg_power:.1f} W")
        print(f"  Peak power: {ct_peak_power:.1f} W")
        print(f"  Total energy: {ct_total_energy:.4f} kWh")
        print(f"  Carbontracker reported energy: {carbontracker_simpipe_data['energy'].sum():.4f} kWh")

        energy_diff = abs(ct_total_energy - carbontracker_simpipe_data['energy'].sum())
        print(f"  Energy difference: {energy_diff:.4f} kWh")
    else:
        print("\nNo power data available during Carbontracker period")
        print(f"  Power data range: {power_data['Date'].min()} to {power_data['Date'].max()}")
        print(f"  Carbontracker range: {first_start_dt} to {last_stop_dt}")