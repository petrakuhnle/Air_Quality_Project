"""Dashboard state and the views it produces, based on berlin_2025.json."""

from dataclasses import dataclass, replace

POLLUTANTS = ("NO2", "PM2.5")
REFERENCES = ("in_force", "eu2030", "who")
MODES = ("Hour", "Day")
DAYTYPES = ("weekday", "weekend", "both")
SEASON_MONTHS = {
    "winter": (12, 1, 2), "spring": (3, 4, 5),
    "summer": (6, 7, 8), "autumn": (9, 10, 11),
}


@dataclass(frozen=True)
class State:
    """What the user has selected.

    Attributes:
        pollutants: Pollutants shown, any of POLLUTANTS.
        months: Selected months, 1 to 12.
        days: Selected dates as "YYYY-MM-DD"; empty means the whole month.
        hours: First and last hour of day, 0 to 23.
        mode: "Hour" for the typical day, "Day" for daily means.
        daytype: "weekday", "weekend" or "both".
        stations: Selected station codes; empty means all.
        reference: Level the status is checked against.
    """

    pollutants: tuple = ("NO2", "PM2.5")
    months: tuple = tuple(range(1, 13))
    days: tuple = ()
    hours: tuple = (0, 23)
    mode: str = "Hour"
    daytype: str = "both"
    stations: tuple = ()
    reference: str = "in_force"


class Refused(Exception):
    """A selection the data cannot answer.

    Args:
        reason: Short text shown to the user.
    """

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class BerlinLuft:
    """The dashboard: holds the data and the current selection.

    Args:
        dataset: Contents of berlin_2025.json as a dict.
    """

    def __init__(self, dataset: dict):
        self.d = dataset
        self.station_codes = tuple(s["code"] for s in dataset["stations"])
        self.pm25_stations = tuple(s["code"] for s in dataset["stations"] if s.get("pm25"))
        self.has_hourly = "hourly" in dataset
        self.state = State(stations=self.station_codes)

    def select(self, **changes) -> None:
        """Change the selection.

        Args:
            **changes: Fields of State to change, e.g. months=(3,), mode="Day".

        Raises:
            Refused: If the new selection cannot be answered from the data.
        """
        new = replace(self.state, **changes)
        self._check(new)
        self.state = new

    def _check(self, s: State) -> None:
        """Validate a selection.

        Args:
            s: Selection to check.

        Raises:
            Refused: With the reason the selection is not possible.
        """
        if not s.pollutants or not set(s.pollutants) <= set(POLLUTANTS):
            raise Refused("unknown pollutant")
        if s.mode not in MODES:
            raise Refused("unknown view")
        if s.daytype not in DAYTYPES:
            raise Refused("unknown day type")
        if s.reference not in REFERENCES:
            raise Refused("unknown reference level")
        if not s.months or not set(s.months) <= set(range(1, 13)):
            raise Refused("month out of range")
        lo, hi = s.hours
        if not 0 <= lo <= hi <= 23:
            raise Refused("hours must be between 0 and 23")
        if s.days and len(s.months) != 1:
            raise Refused("pick days within one month")
        if s.mode == "Day" and s.hours != (0, 23):
            raise Refused("the day view uses whole days, not an hour range")

    def _stations(self, pollutant: str) -> tuple:
        """Selected stations that measure a pollutant.

        Args:
            pollutant: "NO2" or "PM2.5".

        Returns:
            Station codes.
        """
        chosen = self.state.stations or self.station_codes
        if pollutant == "PM2.5":
            return tuple(c for c in chosen if c in self.pm25_stations)
        return tuple(chosen)

    def graph_1(self) -> dict:
        """Line chart data: typical day by hour, or daily means.

        Returns:
            {pollutant: {station: series}}. In Hour mode a series is
            {daytype: [values for the hour range]}; in Day mode it is
            {date: value}.
        """
        s = self.state
        out = {}
        for p in s.pollutants:
            out[p] = {}
            for st in self._stations(p):
                if s.mode == "Hour":
                    prof = self.d["hour_profile"][st][p]
                    dts = ["weekday", "weekend"] if s.daytype == "both" else [s.daytype]
                    out[p][st] = {dt: prof[dt][s.hours[0]:s.hours[1] + 1] for dt in dts}
                else:
                    daily = self.d["daily_mean"][st][p]
                    out[p][st] = {d: v for d, v in sorted(daily.items())
                                  if int(d[5:7]) in s.months and (not s.days or d in s.days)}
        return out

    def graph_2(self) -> dict:
        """Bar chart data: monthly means, or the season mean for a full season.

        Returns:
            {pollutant: {station: {month or season: value}}}.
        """
        s = self.state
        season = next((name for name, ms in SEASON_MONTHS.items()
                       if set(ms) == set(s.months)), None)
        out = {}
        for p in s.pollutants:
            out[p] = {}
            for st in self._stations(p):
                if season:
                    out[p][st] = {season: self.d["season_mean"][st][p][season]}
                else:
                    months = self.d["month_mean"][st][p]
                    out[p][st] = {m: months[m - 1] for m in sorted(s.months)}
        return out

    def quick_values(self) -> dict:
        """Lowest and highest hourly value for the selection.

        Returns:
            Not implemented until hourly values are in the export.

        Raises:
            Refused: While the export holds no hourly values.
        """
        if not self.has_hourly:
            raise Refused("hourly values are not in the export yet")
        raise NotImplementedError

    def highlight(self) -> list[str]:
        """Stations to highlight on the map.

        Returns:
            Selected station codes.
        """
        return list(self.state.stations or self.station_codes)

    def coverage(self) -> float | None:
        """Mean share of valid hours over the selected stations and pollutants.

        Returns:
            Share from 0 to 1, or None if nothing is selected.
        """
        vals = [self.d["coverage"][st][p]
                for p in self.state.pollutants for st in self._stations(p)]
        return round(sum(vals) / len(vals), 4) if vals else None