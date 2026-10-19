
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent
FLIGHT_FILE = BASE_DIR / "flights_sample_3m.csv"

columns = [
    "FL_DATE",
    "AIRLINE",
    "ORIGIN",
    "DEST",
    "DEP_DELAY",
    "ARR_DELAY",
    "CANCELLED",
    "DIVERTED",
    "DELAY_DUE_CARRIER",
    "DELAY_DUE_WEATHER",
    "DELAY_DUE_NAS",
    "DELAY_DUE_SECURITY",
    "DELAY_DUE_LATE_AIRCRAFT",
]

print("Reading selected flight columns...")

df = pd.read_csv(
    FLIGHT_FILE,
    usecols=columns,
    low_memory=False
)

print("\nDATASET SIZE")
print(f"Flight records: {len(df):,}")
print(f"Airlines: {df['AIRLINE'].nunique():,}")
print(f"Routes: {df[['ORIGIN', 'DEST']].drop_duplicates().shape[0]:,}")

print("\nFLIGHT PERFORMANCE")
print(f"Cancellation rate: {df['CANCELLED'].mean() * 100:.2f}%")
print(f"Diversion rate: {df['DIVERTED'].mean() * 100:.2f}%")
print(f"Average departure delay: {df['DEP_DELAY'].mean():.2f} minutes")
print(f"Average arrival delay: {df['ARR_DELAY'].mean():.2f} minutes")

print("\nFLIGHTS BY AIRLINE")
airline_summary = (
    df.groupby("AIRLINE")
    .agg(
        Flights=("AIRLINE", "size"),
        Cancellation_Rate=("CANCELLED", "mean"),
        Avg_Departure_Delay=("DEP_DELAY", "mean"),
        Avg_Arrival_Delay=("ARR_DELAY", "mean"),
    )
    .sort_values("Flights", ascending=False)
)

airline_summary["Cancellation_Rate"] *= 100

print(airline_summary.round(2).to_string())

print("\nDELAY CAUSES")
delay_columns = [
    "DELAY_DUE_CARRIER",
    "DELAY_DUE_WEATHER",
    "DELAY_DUE_NAS",
    "DELAY_DUE_SECURITY",
    "DELAY_DUE_LATE_AIRCRAFT",
]

print(df[delay_columns].sum().sort_values(ascending=False).round(0))

print("\nAnalysis complete.")

# --------------------------------------------------
# EXPORT SUMMARIES FOR THE DASHBOARD
# --------------------------------------------------

OUTPUT_DIR = BASE_DIR / "dashboard_data"
OUTPUT_DIR.mkdir(exist_ok=True)

# 1. Airline performance
airline_summary.to_csv(
    OUTPUT_DIR / "airline_summary.csv"
)

# 2. Monthly flight trends
df["FL_DATE"] = pd.to_datetime(
    df["FL_DATE"], errors="coerce"
)

df["Month"] = df["FL_DATE"].dt.to_period("M").astype(str)

monthly_summary = (
    df.groupby("Month")
    .agg(
        Flights=("AIRLINE", "size"),
        Cancellation_Rate=("CANCELLED", "mean"),
        Avg_Departure_Delay=("DEP_DELAY", "mean"),
        Avg_Arrival_Delay=("ARR_DELAY", "mean"),
    )
    .reset_index()
)

monthly_summary["Cancellation_Rate"] *= 100

monthly_summary.to_csv(
    OUTPUT_DIR / "monthly_summary.csv",
    index=False
)

# 3. Delay causes
delay_totals = df[delay_columns].sum(min_count=1)

delay_summary = (
    delay_totals
    .rename_axis("Delay Cause")
    .reset_index(name="Reported Delay Minutes")
)

delay_summary = delay_summary.dropna(
    subset=["Reported Delay Minutes"]
)

delay_summary.to_csv(
    OUTPUT_DIR / "delay_summary.csv",
    index=False
)

# 4. Most frequent routes
route_summary = (
    df.groupby(["ORIGIN", "DEST"])
    .agg(
        Flights=("AIRLINE", "size"),
        Avg_Arrival_Delay=("ARR_DELAY", "mean"),
        Cancellation_Rate=("CANCELLED", "mean"),
    )
    .reset_index()
    .sort_values("Flights", ascending=False)
    .head(100)
)

route_summary["Cancellation_Rate"] *= 100

route_summary.to_csv(
    OUTPUT_DIR / "route_summary.csv",
    index=False
)

print("\nDashboard summary files saved in:", OUTPUT_DIR)
print("Created: airline_summary.csv")
print("Created: monthly_summary.csv")
print("Created: delay_summary.csv")
print("Created: route_summary.csv")
