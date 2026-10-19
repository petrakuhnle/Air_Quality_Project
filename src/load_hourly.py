"""
Adapter: data/processed/hourly.csv -> tidy table for export_berlin_2025.export().

Input columns (from the file):
    datetime (ISO with UTC offset), station, core, component, period, value, fireworks
Output columns:
    station, pollutant, timestamp (Europe/Berlin), value, fireworks
"""
import pandas as pd

# core -> pollutant. Confirmed in notebooks 01 and 03: PM2.5 is stored as "pm2".
CORE_TO_POLLUTANT = {"no2": "NO2", "pm2": "PM2.5"}


def read_hourly(path: str = "data/processed/hourly.csv") -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"station": str, "core": str, "component": str,
                                  "period": str})
    # Keep hourly rows only; "period" is "1h" for hourly values.
    df = df[df["period"] == "1h"].copy()
    unknown = set(df["core"].str.lower()) - set(CORE_TO_POLLUTANT)
    if unknown:
        raise ValueError(f"unmapped core values: {sorted(unknown)}")
    df["pollutant"] = df["core"].str.lower().map(CORE_TO_POLLUTANT)
    # hourly.csv is already in Berlin time with the hour-start shift applied
    # (notebook 01, cell 14). Do not shift again.
    # Offsets differ between CET and CEST; parse as UTC, then convert.
    df["timestamp"] = pd.to_datetime(df["datetime"], utc=True).dt.tz_convert("Europe/Berlin")
    df["fireworks"] = df["fireworks"].astype(str).str.lower().eq("true")
    df = df.dropna(subset=["value"])
    return df[["station", "pollutant", "timestamp", "value", "fireworks"]]


if __name__ == "__main__":
    h = read_hourly()
    print(h.head())
    print(h.dtypes)
    print("rows:", len(h), "stations:", h["station"].nunique(),
          "pollutants:", sorted(h["pollutant"].unique()))
