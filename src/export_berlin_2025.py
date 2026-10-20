"""Export the 2025 aggregates used by the dashboard to one JSON file.

The input is the cleaned hourly table from notebook 01 (see load_hourly.py).
All values in the JSON are computed here from that table.
"""

import json

import numpy as np
import pandas as pd

POLLUTANTS = ["NO2", "PM2.5"]
MIN_VALID_HOURS = 18
HOURS_IN_YEAR = 8760

# Reference levels in µg/m³, as in the README
LIMITS = {
    "NO2": {
        "annual_in_force": 40, "annual_eu2030": 20, "annual_who": 10,
        "hourly_200": 200,
        "daily_eu2030": 50, "daily_eu2030_allowed": 18,
        "daily_who": 25, "daily_who_allowed": 4,
    },
    "PM2.5": {
        "annual_in_force": 25, "annual_eu2030": 10, "annual_who": 5,
        "daily_eu2030": 25, "daily_eu2030_allowed": 18,
        "daily_who": 15, "daily_who_allowed": 4,
    },
}

# Street names and station types, same as notebook 02
STATION_NAME = {
    "mc010": "Amrumer Str., Wedding",
    "mc027": "Schichauweg, Marienfelde",
    "mc032": "Grunewald, Charlottenburg-Wilmersdorf",
    "mc042": "Nansenstr., Neukölln",
    "mc077": "Buch, Pankow",
    "mc085": "Friedrichshagen, Treptow-Köpenick",
    "mc117": "Schildhornstr., Steglitz",
    "mc124": "Mariendorfer Damm, Mariendorf",
    "mc144": "Silbersteinstr., Neukölln",
    "mc145": "Frohnau, Reinickendorf",
    "mc171": "Brückenstr., Mitte",
    "mc174": "Frankfurter Allee, Friedrichshain",
    "mc190": "Leipziger Str., Mitte",
    "mc221": "Karl-Marx-Str., Neukölln",
    "mc282": "Karlshorst, Lichtenberg",
}
STATION_TYPE = {
    "mc010": "background", "mc042": "background",
    "mc171": "background", "mc282": "background",
    "mc027": "suburb", "mc032": "suburb", "mc077": "suburb",
    "mc085": "suburb", "mc145": "suburb",
    "mc117": "traffic", "mc124": "traffic", "mc144": "traffic",
    "mc174": "traffic", "mc190": "traffic", "mc221": "traffic",
}

SEASON = {
    12: "winter", 1: "winter", 2: "winter",
    3: "spring", 4: "spring", 5: "spring",
    6: "summer", 7: "summer", 8: "summer",
    9: "autumn", 10: "autumn", 11: "autumn",
}


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two points.

    Args:
        lat1: Latitude of the first point, WGS84 degrees.
        lng1: Longitude of the first point, WGS84 degrees.
        lat2: Latitude of the second point, WGS84 degrees.
        lng2: Longitude of the second point, WGS84 degrees.

    Returns:
        Distance in km.
    """
    la1, lo1, la2, lo2 = map(np.radians, [lat1, lng1, lat2, lng2])
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return float(6371 * 2 * np.arcsin(np.sqrt(a)))


def simplify(ring: list, tolerance: float) -> list:
    """Reduce the points of a line, keeping its shape (Ramer-Douglas-Peucker).

    Args:
        ring: Points as [lng, lat] pairs.
        tolerance: Largest allowed deviation, in degrees.

    Returns:
        The kept points, first and last included.
    """
    if len(ring) < 3:
        return ring
    keep = [False] * len(ring)
    keep[0] = keep[-1] = True
    stack = [(0, len(ring) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = ring[a], ring[b]
        dx, dy = x2 - x1, y2 - y1
        norm = (dx * dx + dy * dy) ** 0.5
        best, far = -1.0, None
        for i in range(a + 1, b):
            x, y = ring[i]
            d = (abs(dy * x - dx * y + x2 * y1 - y2 * x1) / norm if norm
                 else ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5)
            if d > best:
                best, far = d, i
        if far is not None and best > tolerance:
            keep[far] = True
            stack += [(a, far), (far, b)]
    return [pt for pt, k in zip(ring, keep, strict=True) if k]


def berlin_outline(boundary_json: str | None, tolerance: float = 0.002) -> list:
    """Outer rings of Berlin's boundary, simplified for a small map.

    The boundary is the OpenStreetMap shape cached by notebook 04.

    Args:
        boundary_json: Path to data/raw/berlin_boundary.json, or None.
        tolerance: Simplification tolerance in degrees (0.002 is about 150 m).

    Returns:
        A list of rings, each a list of [lng, lat] pairs rounded to 4 decimals.
    """
    if not boundary_json:
        return []
    with open(boundary_json, encoding="utf-8") as f:
        shape = json.load(f)
    parts = shape["coordinates"] if shape["type"] == "MultiPolygon" else [shape["coordinates"]]
    rings = []
    for part in parts:
        ring = simplify([list(map(float, pt)) for pt in part[0]], tolerance)
        rings.append([[round(x, 4), round(y, 4)] for x, y in ring])
    return rings


def station_metadata(stations: list[str], df: pd.DataFrame,
                     stations_json: str | None) -> list[dict]:
    """Build the station list for the dashboard.

    Coordinates and measuring height come from the cached API response.
    Missing fields stay None.

    Args:
        stations: Station codes present in the data, e.g. ["mc010", ...].
        df: Hourly table with columns station and pollutant.
        stations_json: Path to raw/stations.json, or None to skip coordinates.

    Returns:
        One dict per station with code, name, type, lat, lng,
        inlet_height_m, pm25 and distance_nearest_km.
    """
    api = {}
    if stations_json:
        with open(stations_json, encoding="utf-8") as f:
            api = {s["code"]: s for s in json.load(f)}

    rows = []
    for code in stations:
        s = api.get(code, {})
        rows.append({
            "code": code,
            "name": STATION_NAME.get(code),
            "type": STATION_TYPE.get(code),
            "lat": float(s["lat"]) if s.get("lat") is not None else None,
            "lng": float(s["lng"]) if s.get("lng") is not None else None,
            "inlet_height_m": s.get("measuringHeight"),
            "pm25": bool((df.loc[df["station"] == code, "pollutant"] == "PM2.5").any()),
        })

    # Nearest other station, as in notebook 04
    located = [r for r in rows if r["lat"] is not None]
    for r in rows:
        others = [haversine_km(r["lat"], r["lng"], o["lat"], o["lng"])
                  for o in located if o["code"] != r["code"]] if r["lat"] is not None else []
        r["distance_nearest_km"] = round(min(others), 1) if others else None
    return rows


def export(hourly: pd.DataFrame, path: str = "berlin_2025.json",
           stations_json: str | None = None, boundary_json: str | None = None) -> dict:
    """Compute the dashboard aggregates and write them to JSON.

    Args:
        hourly: Cleaned hourly table with columns station, pollutant
            ("NO2" or "PM2.5"), timestamp (tz-aware) and value (µg/m³).
        path: Output file.
        stations_json: Path to raw/stations.json for coordinates and height.
        boundary_json: Path to raw/berlin_boundary.json for the map outline.

    Returns:
        The exported data as a dict.
    """
    df = hourly.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_convert("Europe/Berlin")
    df = df[(df["timestamp"].dt.year == 2025) & df["pollutant"].isin(POLLUTANTS)]
    df = df.dropna(subset=["value"])
    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    df["month"] = df["timestamp"].dt.month
    df["daytype"] = np.where(df["timestamp"].dt.dayofweek >= 5, "weekend", "weekday")
    df["season"] = df["month"].map(SEASON)

    stations = sorted(df["station"].unique())

    # Days with fewer than 18 valid hours are dropped (EU 75 % rule).
    # hourly.csv is already filtered in 01, so this normally removes nothing.
    n = df.groupby(["station", "pollutant", "date"]).size().rename("n").reset_index()
    keep = n.loc[n["n"] >= MIN_VALID_HOURS, ["station", "pollutant", "date"]]
    df = df.merge(keep, on=["station", "pollutant", "date"])

    # Share of the year's hours with a value
    counts = df.groupby(["station", "pollutant"]).size()
    coverage = {s: {p: round(float(counts[(s, p)]) / HOURS_IN_YEAR, 4) if (s, p) in counts.index else None
                    for p in POLLUTANTS}
                for s in stations}

    # Mean by hour of day, weekday and weekend separately
    prof = df.groupby(["station", "pollutant", "daytype", "hour"])["value"].mean()
    hour_profile = {
        s: {p: {dt: [round(float(prof[(s, p, dt, h)]), 2) if (s, p, dt, h) in prof.index else None
                     for h in range(24)]
                for dt in ["weekday", "weekend"]}
            for p in POLLUTANTS}
        for s in stations
    }

    # Mean and count by month, day type and hour, so the dashboard can show
    # the hour-of-day profile for any set of months (count-weighted mean)
    pm = df.groupby(["station", "pollutant", "month", "daytype", "hour"])["value"].agg(["mean", "size"])
    hour_profile_month = {s: {p: {} for p in POLLUTANTS} for s in stations}
    for (s, p, m, dt, h), row in pm.iterrows():
        cell = hour_profile_month[s][p].setdefault(str(m), {
            "weekday": {"mean": [None] * 24, "n": [0] * 24},
            "weekend": {"mean": [None] * 24, "n": [0] * 24},
        })
        cell[dt]["mean"][h] = round(float(row["mean"]), 2)
        cell[dt]["n"][h] = int(row["size"])

    # Lowest and highest hour per month and day type, with the hour it was measured
    extremes = {s: {p: {} for p in POLLUTANTS} for s in stations}
    for (s, p, m, dt), g in df.groupby(["station", "pollutant", "month", "daytype"]):
        lo, hi = g.loc[g["value"].idxmin()], g.loc[g["value"].idxmax()]
        fw = g["fireworks"] if "fireworks" in g else pd.Series(False, index=g.index)
        extremes[s][p].setdefault(str(m), {})[dt] = {
            "min": [float(lo["value"]), lo["timestamp"].strftime("%Y-%m-%dT%H:00"), bool(fw[lo.name])],
            "max": [float(hi["value"]), hi["timestamp"].strftime("%Y-%m-%dT%H:00"), bool(fw[hi.name])],
        }

    # Hours in each month and day type, for coverage (March 743, October 745)
    slots = pd.date_range("2025-01-01 00:00", "2025-12-31 23:00", freq="h", tz="Europe/Berlin")
    kind = np.where(slots.dayofweek >= 5, "weekend", "weekday")
    per = pd.Series(1, index=pd.MultiIndex.from_arrays([slots.month, kind])).groupby(level=[0, 1]).sum()
    hours_in_period = {str(m): {dt: int(per.get((m, dt), 0)) for dt in ["weekday", "weekend"]}
                       for m in range(1, 13)}

    # Monthly and seasonal means
    mon = df.groupby(["station", "pollutant", "month"])["value"].mean()
    month_mean = {
        s: {p: [round(float(mon[(s, p, m)]), 2) if (s, p, m) in mon.index else None
                for m in range(1, 13)]
            for p in POLLUTANTS}
        for s in stations
    }
    sea = df.groupby(["station", "pollutant", "season"])["value"].mean()
    season_mean = {
        s: {p: {se: round(float(sea[(s, p, se)]), 2) if (s, p, se) in sea.index else None
                for se in ["winter", "spring", "summer", "autumn"]}
            for p in POLLUTANTS}
        for s in stations
    }

    # Daily means, used by the day picker and the day view
    day = df.groupby(["station", "pollutant", "date"])["value"].mean().round(2)
    daily_mean = {s: {p: {} for p in POLLUTANTS} for s in stations}
    for (s, p, d), v in day.items():
        daily_mean[s][p][d.isoformat()] = float(v)

    # Annual means
    ann = df.groupby(["station", "pollutant"])["value"].mean().round(2)
    annual_mean = {s: {p: float(ann[(s, p)]) if (s, p) in ann.index else None for p in POLLUTANTS}
                   for s in stations}

    # Top 10 % of station x hour-of-day means, cutoff per pollutant (as in 02)
    # Stations without a sensor for a pollutant get None, not 0
    measured = {p: set(df.loc[df["pollutant"] == p, "station"]) for p in POLLUTANTS}

    top10 = {}
    for p in POLLUTANTS:
        m = df[df["pollutant"] == p].groupby(["station", "hour"])["value"].mean()
        top = m[m >= m.quantile(0.90)].groupby(level="station").size()
        top10[p] = {s: int(top.get(s, 0)) if s in measured[p] else None for s in stations}

    # Hours and days above each level
    limits = {}
    for p in POLLUTANTS:
        lim = LIMITS[p]
        sub = df[df["pollutant"] == p]
        daily = sub.groupby(["station", "date"])["value"].mean()
        entry = dict(lim)
        if p == "NO2":
            above = sub[sub["value"] > lim["hourly_200"]].groupby("station").size()
            entry["hours_over_200"] = {s: int(above.get(s, 0)) if s in measured[p] else None
                                       for s in stations}
        eu = (daily > lim["daily_eu2030"]).groupby(level="station").sum()
        who = (daily > lim["daily_who"]).groupby(level="station").sum()
        entry["days_over_eu2030"] = {s: int(eu.get(s, 0)) if s in measured[p] else None
                                     for s in stations}
        entry["days_over_who"] = {s: int(who.get(s, 0)) if s in measured[p] else None
                                  for s in stations}
        limits[p] = entry

    out = {
        "meta": {
            "source": "luftdaten.berlin.de, Berliner Luftgütemessnetz, SenMVKU",
            "license": "dl-de/by-2-0",
            "period": "2025-01-01/2025-12-31",
            "timezone": "Europe/Berlin",
            "pollutants": POLLUTANTS,
            "rule_excluded_day": "fewer than 18 valid hours",
        },
        "stations": station_metadata(stations, df, stations_json),
        "boundary": berlin_outline(boundary_json),
        "hours_in_period": hours_in_period,
        "extremes": extremes,
        "coverage": coverage,
        "annual_mean": annual_mean,
        "hour_profile": hour_profile,
        "hour_profile_month": hour_profile_month,
        "month_mean": month_mean,
        "season_mean": season_mean,
        "daily_mean": daily_mean,
        "top10_hours": top10,
        "limits": limits,
        "note": "Measured values only. Level labels off until LQI bands are confirmed.",
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    return out
