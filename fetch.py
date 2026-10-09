"""Fetch hourly NO2 and PM2.5, 15 BLUME stations, 2025, from luftdaten.berlin.de.

Usage: uv run python fetch.py
"""

import subprocess
import time
from pathlib import Path

RAW = Path(__file__).parent / "raw"

# True = station measures PM2.5
STATIONS = {
    "mc010": True, "mc042": True, "mc171": True, "mc282": False,
    "mc027": False, "mc032": True, "mc077": True, "mc085": True, "mc145": False,
    "mc117": True, "mc124": True, "mc144": True, "mc174": True, "mc190": True, "mc221": True,
}

URL = (
    "https://luftdaten.berlin.de/api/stations/{station}/data"
    "?core={core}&period=1h&timespan=custom"
    "&start%5Bdate%5D={start}&start%5Bhour%5D=1"
    "&end%5Bdate%5D={end}&end%5Bhour%5D=0"
)


def main():
    RAW.mkdir(exist_ok=True)
    for month in range(1, 13):                      # API returns max. one month per request
        start = f"01.{month:02d}.2025"
        end = f"01.{month + 1:02d}.2025" if month < 12 else "01.01.2026"
        for station, has_pm25 in STATIONS.items():
            for core in ["no2", "pm2"] if has_pm25 else ["no2"]:
                path = RAW / f"2025-{month:02d}_{station}_{core}.json"
                if path.exists() and path.stat().st_size > 2:   # cached; "[]" counts as missing
                    continue
                url = URL.format(station=station, core=core, start=start, end=end)
                subprocess.run(["curl", "-s", url, "-o", str(path)], check=True)   # urllib fails on macOS certificates
                time.sleep(0.5)
        print("month", month, "done")


if __name__ == "__main__":
    main()