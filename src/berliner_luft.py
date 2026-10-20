"""Selection model of the Berliner Luft dashboard, in Python.

Mirrors the logic in app/index.html so the numbers on screen can be
reproduced and tested from berlin_2025.json.
"""

from dataclasses import dataclass, field, replace

POLLUTANTS = ("NO2", "PM2.5")
DAYTYPES = ("both", "weekday", "weekend")
VIEWS = ("hour", "month")
TYPES = ("traffic", "background", "suburb")
# Ordered from lowest to highest value
REFERENCES = (("annual_who", "WHO"), ("annual_eu2030", "EU 2030"), ("annual_in_force", "EU now"))


@dataclass(frozen=True)
class Selection:
    """What the user has chosen.

    Attributes:
        stations: Selected station codes; may be empty.
        month: 1 to 12, or None for the full year.
        daytype: "both", "weekday" or "weekend".
        view: "hour" for hour of day, "month" for the year by month.
    """

    stations: frozenset = field(default_factory=lambda: frozenset({"mc174"}))
    month: int | None = None
    daytype: str = "both"
    view: str = "hour"


class BerlinerLuft:
    """The dashboard's data and current selection.

    Args:
        dataset: Contents of berlin_2025.json as a dict.
    """

    def __init__(self, dataset: dict):
        self.d = dataset
        self.codes = tuple(s["code"] for s in dataset["stations"])
        self.meta = {s["code"]: s for s in dataset["stations"]}
        start = frozenset({"mc174"}) if "mc174" in self.codes else frozenset(self.codes[:1])
        self.sel = Selection(stations=start)

    # ---------- selection ----------

    def select(self, **changes) -> None:
        """Change the selection.

        Args:
            **changes: Fields of Selection, e.g. month=3, daytype="weekday".

        Raises:
            ValueError: If a value is not one the dashboard offers.
        """
        new = replace(self.sel, **changes)
        if not set(new.stations) <= set(self.codes):
            raise ValueError("unknown station")
        if new.month is not None and new.month not in range(1, 13):
            raise ValueError("month must be 1 to 12 or None")
        if new.daytype not in DAYTYPES:
            raise ValueError("unknown day type")
        if new.view not in VIEWS:
            raise ValueError("unknown view")
        self.sel = new

    def select_group(self, group: str) -> None:
        """Select all stations, one station type, or none.

        Args:
            group: "all", "none", or a station type ("traffic", "background", "suburb").

        Raises:
            ValueError: If the group is unknown.
        """
        if group == "all":
            codes = self.codes
        elif group == "none":
            codes = ()
        elif group in TYPES:
            codes = tuple(c for c in self.codes if self.meta[c]["type"] == group)
        else:
            raise ValueError("unknown group")
        self.select(stations=frozenset(codes))

    def select_one(self, code: str) -> None:
        """Select one station alone; selecting it again clears the selection.

        Args:
            code: Station code, e.g. "mc174".
        """
        alone = self.sel.stations == frozenset({code})
        self.select(stations=frozenset() if alone else frozenset({code}))

    def select_month(self, month: int) -> None:
        """Select a month; selecting it again returns to the full year.

        Args:
            month: 1 to 12.
        """
        self.select(month=None if self.sel.month == month else month)

    # ---------- helpers ----------

    def measures(self, code: str, pollutant: str) -> bool:
        """Whether a station measures a pollutant.

        Args:
            code: Station code.
            pollutant: "NO2" or "PM2.5".

        Returns:
            True if the station has data for it.
        """
        return pollutant == "NO2" or bool(self.meta[code].get("pm25"))

    def selected(self, pollutant: str | None = None) -> list[str]:
        """Selected stations in list order, optionally only those measuring a pollutant.

        Args:
            pollutant: "NO2", "PM2.5" or None for all selected.

        Returns:
            Station codes.
        """
        return [c for c in self.codes if c in self.sel.stations and (pollutant is None or self.measures(c, pollutant))]

    def _months(self) -> list[int]:
        return [self.sel.month] if self.sel.month else list(range(1, 13))

    def _daytypes(self) -> list[str]:
        return ["weekday", "weekend"] if self.sel.daytype == "both" else [self.sel.daytype]

    def _cells(self, code: str, pollutant: str, months: list[int]) -> list[dict]:
        prof = self.d["hour_profile_month"][code][pollutant]
        return [prof[str(m)][dt] for m in months if str(m) in prof for dt in self._daytypes()]

    def period_mean(self, code: str, pollutant: str, months: list[int] | None = None) -> tuple[float | None, int]:
        """Count-weighted mean of all selected hours for one station.

        For the full year and all days this equals the annual mean.

        Args:
            code: Station code.
            pollutant: "NO2" or "PM2.5".
            months: Months to include; defaults to the selected period.

        Returns:
            (mean in µg/m³ or None, number of valid hours).
        """
        s = n = 0
        for c in self._cells(code, pollutant, months or self._months()):
            for v, k in zip(c["mean"], c["n"], strict=True):
                if v is not None:
                    s += v * k
                    n += k
        return (s / n if n else None, n)

    @staticmethod
    def _mean(values: list) -> float | None:
        vals = [v for v in values if v is not None]
        return sum(vals) / len(vals) if vals else None

    # ---------- views ----------

    def hour_profile(self) -> dict:
        """Hour-of-day chart: mean of the selected stations for each hour.

        Returns:
            {pollutant: [24 values or None]}; pollutants no selected station measures are left out.
        """
        out = {}
        for p in POLLUTANTS:
            codes = self.selected(p)
            if not codes:
                continue
            per = []
            for c in codes:
                row = []
                cells = self._cells(c, p, self._months())
                for h in range(24):
                    s = sum(x["mean"][h] * x["n"][h] for x in cells if x["mean"][h] is not None)
                    n = sum(x["n"][h] for x in cells if x["mean"][h] is not None)
                    row.append(s / n if n else None)
                per.append(row)
            out[p] = [self._mean([r[h] for r in per]) for h in range(24)]
        return out

    def month_profile(self) -> dict:
        """Year chart: mean of the selected stations for each month, all 12 shown.

        Returns:
            {pollutant: [12 values or None]}.
        """
        out = {}
        for p in POLLUTANTS:
            codes = self.selected(p)
            if codes:
                out[p] = [self._mean([self.period_mean(c, p, [m])[0] for c in codes]) for m in range(1, 13)]
        return out

    def limits_table(self) -> list[dict]:
        """Limits chart: every station's mean for the selected period, sorted by NO2.

        Returns:
            Rows with code, selected, and per pollutant the mean and the levels it is above.
        """
        rows = []
        for c in self.codes:
            row = {"code": c, "selected": c in self.sel.stations}
            for p in POLLUTANTS:
                v = self.period_mean(c, p)[0] if self.measures(c, p) else None
                above = [name for key, name in REFERENCES if v is not None and v > self.d["limits"][p][key]]
                row[p] = {"mean": v, "above": above}
            rows.append(row)
        return sorted(rows, key=lambda r: -(r["NO2"]["mean"] or -1))

    def quick_values(self) -> dict:
        """Lowest and highest hour in the selection.

        Returns:
            {pollutant: {"min": (value, time, station, fireworks), "max": (...)}}.
        """
        out = {}
        for p in POLLUTANTS:
            lo = hi = None
            for c in self.selected(p):
                for m in self._months():
                    for dt in self._daytypes():
                        e = self.d["extremes"][c][p].get(str(m), {}).get(dt)
                        if not e:
                            continue
                        if lo is None or e["min"][0] < lo[0]:
                            lo = (e["min"][0], e["min"][1], c, e["min"][2])
                        if hi is None or e["max"][0] > hi[0]:
                            hi = (e["max"][0], e["max"][1], c, e["max"][2])
            if lo:
                out[p] = {"min": lo, "max": hi}
        return out

    def coverage(self) -> dict:
        """Share of possible hours with a valid value, over the selected stations.

        Returns:
            {pollutant: share from 0 to 1}.
        """
        possible = sum(self.d["hours_in_period"][str(m)][dt] for m in self._months() for dt in self._daytypes())
        out = {}
        for p in POLLUTANTS:
            codes = self.selected(p)
            if codes:
                out[p] = sum(self.period_mean(c, p)[1] for c in codes) / (possible * len(codes))
        return out

    def missing_pm25(self) -> list[str]:
        """Selected stations without a PM2.5 sensor, for the note at the bottom.

        Returns:
            Station codes.
        """
        return [c for c in self.selected() if not self.measures(c, "PM2.5")]
