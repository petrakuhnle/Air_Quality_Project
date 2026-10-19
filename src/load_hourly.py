"""Read the cleaned hourly table from notebook 01 for the export."""

import pandas as pd

# PM2.5 is stored as "pm2" in the raw files and in hourly.csv
CORE_TO_POLLUTANT = {"no2": "NO2", "pm2": "PM2.5"}


def read_hourly(path: str = "data/processed/hourly.csv") -> pd.DataFrame:
    """Load hourly.csv and rename columns for export().

    hourly.csv already has short days dropped and timestamps shifted to the
    start of the hour (notebook 01), so no further cleaning is done here.

    Args:
        path: Path to hourly.csv.

    Returns:
        Table with columns station, pollutant, timestamp (Europe/Berlin),
        value and fireworks.

    Raises:
        ValueError: If the file holds a pollutant code not in CORE_TO_POLLUTANT.
    """
    df = pd.read_csv(path, dtype={"station": str, "core": str,
                                  "component": str, "period": str})
    df = df[df["period"] == "1h"].copy()

    unknown = set(df["core"].str.lower()) - set(CORE_TO_POLLUTANT)
    if unknown:
        raise ValueError(f"unknown pollutant codes: {sorted(unknown)}")

    df["pollutant"] = df["core"].str.lower().map(CORE_TO_POLLUTANT)
    # Offsets switch between +01:00 and +02:00; parse as UTC, then convert
    df["timestamp"] = pd.to_datetime(df["datetime"], utc=True).dt.tz_convert("Europe/Berlin")
    df["fireworks"] = df["fireworks"].astype(str).str.lower().eq("true")
    df = df.dropna(subset=["value"])
    return df[["station", "pollutant", "timestamp", "value", "fireworks"]]


if __name__ == "__main__":
    h = read_hourly()
    print(h.head())
    print(len(h), "rows,", h["station"].nunique(), "stations")