"""
Kick Target Mapping (KTM) Analysis for Rugby League
- Collects and analyzes kick event data
- Maps kick types, field zones, outcomes, and context
- Visualizes kick strategies and effectiveness
- Integrates with match prediction models
"""
import subprocess
import sys

# Ensure seaborn is installed
try:
    import seaborn
except ImportError:
    print("[INFO] seaborn not found, installing via pip...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'seaborn'])
    import seaborn

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from datetime import datetime

# 1. Data Collection (from CSV or API)
def collect_kick_data(local_file=None):
    if local_file and os.path.exists(local_file):
        print(f"[INFO] Loading kick data from file: {local_file}")
        df = pd.read_csv(local_file)
        # Diagnostics for coordinate columns
        for col in ['StartX', 'StartY', 'TargetX', 'TargetY']:
            if col in df.columns:
                print(f"[DIAG] {col} min: {df[col].min()}, max: {df[col].max()}, unique: {sorted(df[col].unique())[:10]} ...")
        # Warn if values are outside expected range (0-100)
        for col in ['StartX', 'StartY', 'TargetX', 'TargetY']:
            if col in df.columns and (df[col].min() < 0 or df[col].max() > 100):
                print(f"[WARN] {col} values outside expected 0-100m range! Data may need normalization.")
        return df
    print("[WARN] No kick_events.csv found. Using dummy data! Only 2 kicks will be shown.")
    # Example dummy data for structure
    data = [
        {"KickType": "Bomb", "StartX": 30, "StartY": 40, "TargetX": 10, "TargetY": 5, "Outcome": "DropOut", "Team": "Broncos", "Player": "PlayerA", "Minute": 55, "Score": "12-10", "Pressure": "High"},
        {"KickType": "Grubber", "StartX": 10, "StartY": 5, "TargetX": 0, "TargetY": 0, "Outcome": "Try", "Team": "Broncos", "Player": "PlayerB", "Minute": 78, "Score": "18-16", "Pressure": "High"},
    ]
    return pd.DataFrame(data)

# 2. Define Field Zones
def assign_field_zone(x, y):
    if x <= 20:
        return "0-20m"
    elif x <= 40:
        return "20-40m"
    else:
        return "40m+"

def add_zones(df):
    df['StartZone'] = df.apply(lambda row: assign_field_zone(row['StartX'], row['StartY']), axis=1)
    df['TargetZone'] = df.apply(lambda row: assign_field_zone(row['TargetX'], row['TargetY']), axis=1)
    return df

# 3. Analysis
def analyze_kicks(df):
    summary = df.groupby(['KickType', 'TargetZone', 'Outcome']).size().unstack(fill_value=0)
    print("\n[INFO] Kick Summary Table:")
    print(summary)
    print("\n[INFO] Kick Data Sample:")
    print(df.head(10).to_string(index=False))
    print(f"\n[INFO] Total kicks: {len(df)}")
    print(f"[INFO] Unique kick types: {df['KickType'].unique().tolist()}")
    print(f"[INFO] Unique outcomes: {df['Outcome'].unique().tolist()}")
    return summary

# 4. Visualization
def plot_kick_heatmap(df, outdir):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='TargetX', y='TargetY', hue='KickType', data=df, alpha=0.7)
    plt.title('Kick Target Map')
    plt.xlabel('Field X (m)')
    plt.ylabel('Field Y (m)')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    outpath = os.path.join(outdir, f'kick_target_map_{datetime.now().date()}.png')
    plt.savefig(outpath)
    plt.close()
    print(f"[SUCCESS] Kick target map saved to {outpath}")

# 5. Reporting
def save_kick_report(df, summary, outdir):
    out_csv = os.path.join(outdir, f'kick_report_{datetime.now().date()}.csv')
    out_json = os.path.join(outdir, f'kick_report_{datetime.now().date()}.json')
    df.to_csv(out_csv, index=False)
    summary.to_json(out_json)
    print(f"[SUCCESS] Kick report saved to {out_csv} and {out_json}")

# 6. Integration with Prediction Model (placeholder)
def integrate_with_prediction_model(df):
    # Pass kick effectiveness metrics to your model as needed
    pass

if __name__ == "__main__":
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs'))
    os.makedirs(outputs_dir, exist_ok=True)
    # Replace with your real data source or API
    kick_df = collect_kick_data(local_file=os.path.join(outputs_dir, 'kick_events.csv'))
    # Filter out scaffold/blank rows (no KickType or StartX/TargetX)
    before = len(kick_df)
    kick_df = kick_df[
        kick_df['KickType'].notna() & (kick_df['KickType'] != '') &
        kick_df['StartX'].notna() & kick_df['TargetX'].notna()
    ]
    after = len(kick_df)
    print(f"[INFO] Filtered out {before - after} scaffold/blank rows. {after} real kicks remain.")
    if after == 0:
        print("[WARN] No real kick data found. Please annotate kick_events.csv with real kick events.")
    kick_df = add_zones(kick_df)
    summary = analyze_kicks(kick_df)
    plot_kick_heatmap(kick_df, outputs_dir)
    save_kick_report(kick_df, summary, outputs_dir)
    # integrate_with_prediction_model(kick_df)
