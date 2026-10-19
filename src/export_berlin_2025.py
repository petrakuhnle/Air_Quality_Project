"""
Step 1 · Export berlin_2025.json for the single dashboard.

Input: a tidy hourly table `hourly` with columns
    station (str, e.g. "mc010"), pollutant (str, "NO2" or "PM2.5"),
    timestamp (tz-aware, Europe/Berlin), value (float, µg/m³)
Load it from the cache written in notebook 01 (after drops).
All numbers come from this table; nothing is typed by hand.
"""
import json
import numpy as np
import pandas as pd

POLLUTANTS = ["NO2", "PM2.5"]
MIN_VALID_HOURS = 18
HOURS_IN_YEAR = 8760

# Reference levels from the README (µg/m³)
LIMITS = {
    "NO2":   {"annual_in_force": 40, "annual_eu2030": 20, "annual_who": 10,
              "hourly_200": 200, "daily_eu2030": 50, "daily_eu2030_allowed": 18,
              "daily_who": 25, "daily_who_allowed": 4},
    "PM2.5": {"annual_in_force": 25, "annual_eu2030": 10, "annual_who": 5,
              "daily_eu2030": 25, "daily_eu2030_allowed": 18,
              "daily_who": 15, "daily_who_allowed": 4},
}
SEASON = {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring",
          5: "spring", 6: "summer", 7: "summer", 8: "summer",
          9: "autumn", 10: "autumn", 11: "autumn"}


def export(hourly: pd.DataFrame, path: str = "berlin_2025.json") -> dict:
    df = hourly.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_convert("Europe/Berlin")
    df = df[(df["timestamp"].dt.year == 2025) & df["pollutant"].isin(POLLUTANTS)]
    df = df.dropna(subset=["value"])
    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    df["month"] = df["timestamp"].dt.month
    df["daytype"] = np.where(df["timestamp"].dt.dayofweek >= 5, "weekend", "weekday")

    stations = sorted(df["station"].unique())

    # Coverage and excluded days (rule: fewer than 18 valid hours)
    valid = df.groupby(["station", "pollutant", "date"]).size().rename("n").reset_index()
    kept_days = valid[valid["n"] >= MIN_VALID_HOURS]
    excluded = valid[valid["n"] < MIN_VALID_HOURS]
    df = df.merge(kept_days[["station", "pollutant", "date"]],
                  on=["station", "pollutant", "date"], how="inner")

    coverage = {}
    for s in stations:
        coverage[s] = {}
        for p in POLLUTANTS:
            n = int(((df["station"] == s) & (df["pollutant"] == p)).sum())
            coverage[s][p] = round(n / HOURS_IN_YEAR, 4)

    # Hourly profile per station, pollutant, day type (24 values each)
    prof = df.groupby(["station", "pollutant", "daytype", "hour"])["value"].mean()
    hour_profile = {}
    for s in stations:
        hour_profile[s] = {}
        for p in POLLUTANTS:
            hour_profile[s][p] = {}
            for dt in ["weekday", "weekend"]:
                vals = prof.loc[(s, p, dt)] if (s, p, dt) in prof.index else pd.Series(dtype=float)
                hour_profile[s][p][dt] = [None if h not in vals.index else round(float(vals[h]), 2)
                                          for h in range(24)]

    # Monthly means (12 per station and pollutant)
    mm = df.groupby(["station", "pollutant", "month"])["value"].mean()
    month_mean = {s: {p: [None if (s, p, m) not in mm.index else round(float(mm[(s, p, m)]), 2)
                          for m in range(1, 13)] for p in POLLUTANTS} for s in stations}

    # Seasonal means (Dec counted in winter of 2025, as the method states)
    df["season"] = df["month"].map(SEASON)
    sm = df.groupby(["station", "pollutant", "season"])["value"].mean()
    season_mean = {}
    for s in stations:
        season_mean[s] = {}
        for p in POLLUTANTS:
            season_mean[s][p] = {se: (None if (s, p, se) not in sm.index else round(float(sm[(s, p, se)]), 2))
                                 for se in ["winter", "spring", "summer", "autumn"]}

    # Daily means (365 per station and pollutant at most, for the day picker)
    dm = df.groupby(["station", "pollutant", "date"])["value"].mean().round(2)
    daily_mean = {}
    for s in stations:
        daily_mean[s] = {}
        for p in POLLUTANTS:
            series = dm.loc[(s, p)] if (s, p) in dm.index else pd.Series(dtype=float)
            daily_mean[s][p] = {d.isoformat(): float(v) for d, v in series.items()}

    # Annual means
    annual = df.groupby(["station", "pollutant"])["value"].mean().round(2)
    annual_mean = {s: {p: (None if (s, p) not in annual.index else float(annual[(s, p)]))
                       for p in POLLUTANTS} for s in stations}

    # Top 10% station-hours: station x hour-of-day mean, cutoff = 90th percentile
    # within each pollutant (separate cutoffs, as in notebook 02, cell 4),
    # counted per station.
    top10 = {}
    for p in POLLUTANTS:
        sub = df[df["pollutant"] == p].groupby(["station", "hour"])["value"].mean()
        cut = sub.quantile(0.90)
        counts = sub[sub >= cut].groupby(level="station").size()
        top10[p] = {s: int(counts.get(s, 0)) for s in stations}

    # Hours and days above each reference
    limits_out = {}
    for p in POLLUTANTS:
        lim = LIMITS[p]
        sub = df[df["pollutant"] == p]
        daily = sub.groupby(["station", "date"])["value"].mean()
        entry = {k: v for k, v in lim.items()}
        if p == "NO2":
            hrs = sub[sub["value"] > lim["hourly_200"]].groupby("station").size()
            entry["hours_over_200"] = {s: int(hrs.get(s, 0)) for s in stations}
        entry["days_over_eu2030"] = {s: int((daily.loc[s] > lim["daily_eu2030"]).sum()) if s in daily.index.get_level_values(0) else 0 for s in stations}
        entry["days_over_who"] = {s: int((daily.loc[s] > lim["daily_who"]).sum()) if s in daily.index.get_level_values(0) else 0 for s in stations}
        limits_out[p] = entry

    stations_meta = [{"code": s, "pm25": bool((df[(df["station"] == s)]["pollutant"] == "PM2.5").any())}
                     for s in stations]

    out = {
        "meta": {
            "source": "luftdaten.berlin.de, Berliner Luftgütemessnetz, SenMVKU",
            "license": "dl-de/by-2-0",
            "period": "2025-01-01/2025-12-31",
            "timezone": "Europe/Berlin",
            "pollutants": POLLUTANTS,
            "rule_excluded_day": "fewer than 18 valid hours",
            "excluded_days_count": int(len(excluded)),
        },
        "stations": stations_meta,
        "coverage": coverage,
        "annual_mean": annual_mean,
        "hour_profile": hour_profile,
        "month_mean": month_mean,
        "season_mean": season_mean,
        "daily_mean": daily_mean,
        "top10_hours": top10,
        "limits": limits_out,
        "note": "Measured values only. Level labels off until LQI bands are confirmed.",
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return out


if __name__ == "__main__":
    # Replace with the cached hourly table from notebook 01:
    # hourly = pd.read_parquet("cache/hourly_2025.parquet")
    raise SystemExit("Load `hourly` from notebook 01's cache, then call export(hourly).")
