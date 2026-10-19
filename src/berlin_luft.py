"""
Berliner Luft · object skeleton (data-independent).

Reads the dict produced by export_berlin_2025.py (berlin_2025.json).
quick_values() is refused until hourly values are added to the export.
"""
from dataclasses import dataclass, field, replace

POLLUTANTS = ("NO2", "PM2.5")
REFERENCES = ("in_force", "eu2030", "who")
MODES = ("Hour", "Day")
DAYTYPES = ("weekday", "weekend", "both")
SEASONS = ("winter", "spring", "summer", "autumn")
SEASON_MONTHS = {"winter": (12, 1, 2), "spring": (3, 4, 5),
                 "summer": (6, 7, 8), "autumn": (9, 10, 11)}


@dataclass(frozen=True)
class State:
    pollutants: tuple = ("NO2", "PM2.5")
    months: tuple = tuple(range(1, 13))
    days: tuple = ()                 # empty = whole month
    hours: tuple = (0, 23)
    mode: str = "Hour"
    daytype: str = "both"
    stations: tuple = ()             # empty = all
    reference: str = "in_force"


class Refused(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


class BerlinLuft:
    def __init__(self, dataset: dict):
        self.d = dataset
        self.station_codes = tuple(s["code"] for s in dataset["stations"])
        self.pm25_stations = tuple(s["code"] for s in dataset["stations"] if s.get("pm25"))
        self.has_hourly = "hourly" in dataset          # quick values need this
        self.state = State(stations=self.station_codes)

    # ---- state -------------------------------------------------------
    def select(self, **kw):
        """Change state. Raises Refused(reason) for anything the data cannot answer."""
        new = replace(self.state, **kw)
        self._check(new)
        self.state = new
        return "ok"

    def _check(self, s: State):
        if not set(s.pollutants) <= set(POLLUTANTS) or not s.pollutants:
            raise Refused("unknown pollutant")
        if s.mode not in MODES:
            raise Refused("unknown mode")
        if s.daytype not in DAYTYPES:
            raise Refused("unknown day type")
        if s.reference not in REFERENCES:
            raise Refused("unknown reference")
        if not s.months or not set(s.months) <= set(range(1, 13)):
            raise Refused("month out of range")
        lo, hi = s.hours
        if not (0 <= lo <= hi <= 23):
            raise Refused("hour range out of 0-23")
        if s.days and len(s.months) != 1:
            raise Refused("days need exactly one selected month")
        if s.mode == "Day" and s.hours != (0, 23):
            raise Refused("daily view ignores hour range")

    # ---- outputs -----------------------------------------------------
    def _stations(self):
        return self.state.stations or self.station_codes

    def graph_1(self):
        """Hour: typical day (24 values). Day: daily means for the selection."""
        s, out = self.state, {}
        for p in s.pollutants:
            out[p] = {}
            for st in self._stations():
                if p == "PM2.5" and st not in self.pm25_stations:
                    continue
                if s.mode == "Hour":
                    prof = self.d["hour_profile"][st][p]
                    dts = ["weekday", "weekend"] if s.daytype == "both" else [s.daytype]
                    out[p][st] = {dt: prof[dt][s.hours[0]:s.hours[1] + 1] for dt in dts}
                else:
                    daily = self.d["daily_mean"][st][p]
                    keys = [k for k in daily if int(k[5:7]) in s.months
                            and (not s.days or k in s.days)]
                    out[p][st] = {k: daily[k] for k in sorted(keys)}
        return out

    def graph_2(self):
        """Monthly means, or seasonal means when the selection is a full season."""
        s, out = self.state, {}
        full = [se for se, ms in SEASON_MONTHS.items() if set(ms) == set(s.months)]
        for p in s.pollutants:
            out[p] = {}
            for st in self._stations():
                if p == "PM2.5" and st not in self.pm25_stations:
                    continue
                if full:
                    out[p][st] = {full[0]: self.d["season_mean"][st][p][full[0]]}
                else:
                    mm = self.d["month_mean"][st][p]
                    out[p][st] = {m: mm[m - 1] for m in sorted(s.months)}
        return out

    def quick_values(self):
        if not self.has_hourly:
            raise Refused("hourly values not in dataset; export needed")
        raise NotImplementedError("compute min/max from hourly values once exported")

    def highlight(self):
        return list(self._stations())

    def coverage(self):
        s = self.state
        vals = [self.d["coverage"][st][p] for st in self._stations()
                for p in s.pollutants if not (p == "PM2.5" and st not in self.pm25_stations)]
        return round(sum(vals) / len(vals), 4) if vals else None


# ---- self-test on a minimal fake dataset (structure only) ---------------
if __name__ == "__main__":
    def prof(v): return {"weekday": [v] * 24, "weekend": [v] * 24}
    def pm(v): return {"NO2": v, "PM2.5": v}
    fake = {
        "stations": [{"code": "mc010", "pm25": True}, {"code": "mc282", "pm25": False}],
        "coverage": {"mc010": {"NO2": 0.98, "PM2.5": 0.97}, "mc282": {"NO2": 0.99}},
        "hour_profile": {"mc010": {"NO2": prof(30), "PM2.5": prof(10)},
                         "mc282": {"NO2": prof(20)}},
        "month_mean": {"mc010": {"NO2": [30]*12, "PM2.5": [10]*12},
                       "mc282": {"NO2": [20]*12}},
        "season_mean": {"mc010": {"NO2": {"winter": 33, "spring": 28, "summer": 22, "autumn": 27},
                                   "PM2.5": {"winter": 12, "spring": 9, "summer": 7, "autumn": 10}},
                        "mc282": {"NO2": {"winter": 23, "spring": 18, "summer": 12, "autumn": 17}}},
        "daily_mean": {"mc010": {"NO2": {"2025-03-01": 31, "2025-03-02": 29, "2025-04-01": 27},
                                 "PM2.5": {"2025-03-01": 11}},
                       "mc282": {"NO2": {"2025-03-01": 21}}},
    }
    b = BerlinLuft(fake)
    b.select(months=(3,), mode="Day")
    print("graph_1 day:", b.graph_1()["NO2"]["mc010"])
    b.select(months=(3,), days=("2025-03-01",))
    print("graph_1 days:", b.graph_1()["NO2"]["mc010"])
    b.select(months=(1, 2, 12), days=(), mode="Hour", daytype="weekday", hours=(7, 9))
    print("graph_2 winter:", b.graph_2()["NO2"]["mc010"])
    try:
        b.select(months=(3, 4), days=("2025-03-01",))
    except Refused as e:
        print("refused:", e.reason)
    try:
        b.quick_values()
    except Refused as e:
        print("refused:", e.reason)
    print("coverage:", b.coverage())
