# Air Quality Project

## Project

Berlin air pollution, 2025: when and where are people exposed most?

**Key result.** Nansenstr. and Karl-Marx-Str. are 600 m apart. NO₂: 15.2 and 22.4 µg/m³,
one below the EU limit from 2030 (20), one above it. PM2.5: 12.0 and 13.1, both above the
EU 2030 limit (10). NO₂ changes between neighbouring streets; PM2.5 barely does.

**Dashboard:** [Berliner Luft · Data 2025](https://huggingface.co/spaces/petrakuhnle/berliner-luft)
· hourly measurements 2025, 15 stations, NO₂ and PM2.5, by hour, month and station, against
WHO, EU 2030 and EU limits in force in 2025.

**Questions**

1. Which hours of day and stations have the highest values?
2. Which season is most polluted, and does it differ per station?
3. Which stations have the most hours above the EU 2030 limit values and WHO guideline levels?

**Pollutants:** NO₂, PM2.5 (largest health burden). Ozone excluded: forms in sunlight, highest away from traffic.

**Focus:** location and time of exposure, not causes.

| | Hypothesis | Q | Result |
| --- | --- | --- | --- |
| H1 | Top hours concentrate at a few stations, not spread across Berlin | 1 | Holds for NO₂: the top 10 % of station-hours sit at 5 of 15 stations, all traffic. PM2.5 concentrates too (4 of 12), but the range is narrow |
| H2 | Both pollutants highest in winter, lowest in summer, at all stations | 2 | Holds for PM2.5: all 12 stations peak in February. Fails for NO₂ as stated: 9 of 15 stations peak in March |
| H3 | The same few stations have the most hours above the reference levels, both pollutants | 3 | Partly: the 4 PM2.5 top-decile stations are among the 5 NO₂ top-decile stations, all traffic. A joint ranking of hours above the levels was not computed |

## Findings

**Q1 · Hours and stations** ([02](notebooks/02_peak_hours.ipynb))

- NO₂ swings about 45 % from the 03:00 low to the 07:00 peak. PM2.5 stays within about 10 % all day
- Top 10 % of station-hours: NO₂ at 5 of 15 stations, all traffic. PM2.5 at 4 of 12, in a narrow range
- Between stations, NO₂ spans 7.6 to 26.3 µg/m³ (factor 3.5), PM2.5 8.2 to 13.6 (factor 1.7)
- Weekend NO₂ is 14 to 25 % lower at every station, not only at traffic sites. Weekend PM2.5 moves under 4 %

**Q2 · Seasons** ([03](notebooks/03_seasons.ipynb))

- PM2.5 peaks in February at all 12 stations
- NO₂ peaks in March at 9 of 15 stations (February 4, January 1, November 1). March 2025 had
  exceptional high-pressure weather ([DWD](https://www.dwd.de/DE/presse/pressemitteilungen/DE/2025/20250331_pm_maerz_news.html))
- Share of hours above the WHO level: NO₂ 79.1 % in February, 38.5 % in June. PM2.5 97.8 % in
  February, 67.2 % in September
- Excluding the New Year fireworks lowers January PM2.5 from 11.5 to 11.2 µg/m³. The pattern does not change

**Q3 · Reference levels** ([02](notebooks/02_peak_hours.ipynb), [03](notebooks/03_seasons.ipynb), [04](notebooks/04_spatial.ipynb))

- Annual means: all 15 stations are below the limits in force in 2025
- Against the 2030 limits: 5 of 15 NO₂ and 9 of 12 PM2.5 stations are above
- Against the WHO levels: 10 of 15 NO₂ and all 12 PM2.5 stations are above
- Days above the 24-hour PM2.5 levels: 8 of 12 stations exceed the EU 2030 allowance of 18 days;
  all 12 exceed WHO's 3 to 4 days, with 34 to 107 days

**Between the stations** ([04](notebooks/04_spatial.ipynb))

- The nearest other station is typically 4.6 km away (0.6 to 12.7 km)
- Estimating a station from the others misses NO₂ by 7.1 µg/m³ on average, close to the 10 µg/m³
  gap between the WHO level and the EU 2030 limit. PM2.5: 1.6 µg/m³
- The city model (FAirQ 2025) reads high: +2.9 µg/m³ NO₂, +1.0 PM2.5. NO₂ is above the measurement
  at 14 of 15 stations and

## Data

[luftdaten.berlin.de](https://luftdaten.berlin.de/lqi) · Berliner Luftgütemessnetz, SenMVKU
REST API, JSON · [API docs](https://luftdaten.berlin.de/api/doc) · [open data](https://daten.berlin.de/datensaetze/luftdaten-berlin)
License: [dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0) · Cite: *luftdaten.berlin.de – Berliner Luftgütemessnetz / 2026-10-07; own calculation.*

Measuring height: the pollutant metadata gives a standard height of about 3.5–4 m
above the container roof for NO₂, and no figure for PM2.5
([source](https://luftdaten.berlin.de/pollution/overview)). The API field
`measuringHeight` is filled for 3 of 15 stations (40, 35 and 3) and is undocumented.
40 and 35 lie within Berlin's ground elevation above sea level, so they may not be
inlet heights.

[Active stations](https://luftdaten.berlin.de/station/overview/active):

| Code | Station | Type | PM2.5 |
| --- | --- | --- | --- |
| mc010 | Wedding, Amrumer Straße | background | yes |
| mc042 | Neukölln, Nansenstraße | background | yes |
| mc171 | Mitte, Brückenstraße | background | yes |
| mc282 | Karlshorst | background | no |
| mc027 | Marienfelde, Schichauweg | suburb | no |
| mc032 | Grunewald | suburb | yes |
| mc077 | Buch | suburb | yes |
| mc085 | Friedrichshagen | suburb | yes |
| mc145 | Frohnau | suburb | no |
| mc117 | Schildhornstraße | traffic | yes |
| mc124 | Mariendorfer Damm | traffic | yes |
| mc144 | Silbersteinstraße | traffic | yes |
| mc174 | Frankfurter Allee | traffic | yes |
| mc190 | Leipziger Straße | traffic | yes |
| mc221 | Karl-Marx-Straße | traffic | yes |

## Reference levels

µg/m³

| | Period | EU in force 2025 | Allowed/year | EU from 2030 | Allowed/year | WHO 2021 | Allowed/year |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NO₂ | 1 hour | 200 | 18 | 200 | 3 | – | – |
| NO₂ | 24 hours | – | – | 50 | 18 | 25 | 3–4 days |
| NO₂ | year | 40 | – | 20 | – | 10 | – |
| PM2.5 | 24 hours | – | – | 25 | 18 | 15 | 3–4 days |
| PM2.5 | year | 25 | – | 10 | – | 5 | – |

Sources: in force 2025 · [Directive 2008/50/EC](https://eur-lex.europa.eu/eli/dir/2008/50/oj),
in Germany [39. BImSchV](https://www.gesetze-im-internet.de/bimschv_39/) ·
from 2030 · [Directive (EU) 2024/2881, Annex I](https://eur-lex.europa.eu/eli/dir/2024/2881/oj) ·
[WHO guidelines 2021](https://www.who.int/publications/i/item/9789240034228)

## Sources

| | Source | Licence |
| --- | --- | --- |
| Measurements | [luftdaten.berlin.de](https://luftdaten.berlin.de/), Berliner Luftgütemessnetz, SenMVKU | [dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0) |
| City model | [Digitale Berliner Luftkarte](https://www.berlin.de/sen/uvk/umwelt/luft/luftqualitaet/digitale-berliner-luftkarte/), FAirQ 2025, read through WMS `ua_luftschadstoffbelastung_2025` | dl-de/zero-2-0 |
| Weather, March 2025 | [Deutscher Wetterdienst](https://www.dwd.de/DE/presse/pressemitteilungen/DE/2025/20250331_pm_maerz_news.html) | – |
| Berlin boundary | [OpenStreetMap](https://www.openstreetmap.org/copyright) via Nominatim | ODbL |
| Limits and guidelines | See Reference levels | – |

## Analyses

|  | Compute | Note | Q |
| --- | --- | --- | --- |
| 1 | Top 10% station-hours across all stations, per pollutant | Hour-of-day mean per station × hour; not single maximum | 1 |
| 2 | Count of top station-hours per station | Which stations dominate | 1, 3 |
| 3 | Hour-of-day mean per station, weekday vs. weekend | Traffic signal: NO₂ should drop at weekends, PM2.5 should not | 1 |
| 4 | Annual mean per station vs. EU 2030 and WHO levels | Which stations already fail the level they will be judged by | 3 |
| 5 | Hours above reference levels per station | Hourly value vs. 24-hour level: indicator of exposure, not an exceedance. Only NO₂ 200 is a true hourly limit | 3 |
| 6 | Seasonal mean per station | Seasons: Dec–Feb, Mar–May, Jun–Aug, Sep–Nov | 2 |
| 7 | Days above 24-hour levels vs. allowed per year | Compliance check | 3 |
| 8 | Distance from each station to its nearest neighbour | How dense the network is | 1 |
| 9 | Each station estimated from the others, inverse distance weighting | How far a measurement travels, as an error in µg/m³ | 1, 3 |
| 10 | City model FAirQ 2025 at each station | Model error against the measurement and against the estimate | 3 |
| 11 | City model read every 2 km inside Berlin | Share of the area above each level, against the share of stations | 3 |

## Method

- Hourly values fetched with `fetch.py`: one request per month × station × pollutant (API returns max. one month), 324 JSON files cached in `raw/`, never modified
- Endpoint: `https://luftdaten.berlin.de/api/stations/{station}/data?core={no2|pm2}&period=1h&timespan=custom&...`
- Timestamps with UTC offset → Europe/Berlin
- Timestamps mark end of hour → shifted −1 h to hour start
- All days included (weekdays and weekends)
- Days with <18 valid hours excluded (75 % coverage, EU standard)
- Outliers by type: sensor errors removed; real events (e.g. New Year's fireworks) kept and flagged
- Aggregates (pandas):
    - station × hour mean → top 10% per pollutant, counted per station
    - station × season mean
    - hourly values → hours above reference levels, per station
    - daily means → days above 24-hour levels vs. allowed
- Valid-hour coverage reported per aggregate

## Notebooks

| Notebook | Content |
| --- | --- |
| [01_data](notebooks/01_data.ipynb) | Load, time zone, drops, outliers, coverage, hourly PM2.5 availability |
| [02_peak_hours](notebooks/02_peak_hours.ipynb) | Hour of day, top 10 % station-hours, station ranking against reference levels, weekday vs. weekend, traffic increment |
| [03_seasons](notebooks/03_seasons.ipynb) | Monthly means, hours above the WHO level, days above 24-hour levels, fireworks check |
| [04_spatial](notebooks/04_spatial.ipynb) | Station distances, estimating a station from the others, city model at stations, share of Berlin's area above each level |

## Dashboard

[Berliner Luft · Data 2025](https://huggingface.co/spaces/petrakuhnle/berliner-luft), a static Hugging Face Space.

- **Select:** one station, a station type or all, on the map or in the limits table · one month or the
  full year · all days, Mon–Fri or Sat–Sun
- **Shows:** NO₂ and PM2.5 by hour of day or by month · all stations against the WHO level, the EU 2030
  limit and the EU limit in force in 2025 · lowest and highest hour · share of valid hours
- **Built:** `src/load_hourly.py` reads `data/processed/hourly.csv` → `src/export_berlin_2025.py` writes
  `app/berlin_2025.json` (means and counts per station, month, day type and hour) → `app/index.html`
  computes every view from that file. `src/berliner_luft.py` repeats the page's logic in Python for checks
- **Map outline:** © OpenStreetMap contributors, ODbL

## How to run

    uv sync
    uv run python fetch.py        # only if raw/ is empty
    # run notebooks 01 → 04 in order, then export the dashboard data:
    uv run python -c "import sys; sys.path.insert(0, 'src'); from load_hourly import read_hourly; from export_berlin_2025 import export; export(read_hourly(), 'app/berlin_2025.json', stations_json='data/raw/stations.json', boundary_json='data/raw/berlin_boundary.json')"
    # open the dashboard locally:
    cd app && python3 -m http.server     # then http://localhost:8000

## Stack

Python 3.14 · uv · pandas · numpy · matplotlib · seaborn · dashboard: HTML, CSS and JavaScript, no libraries

## Status

**Phase 1: Setup and project planning**

- [x] Select dataset: suitable dataset found, first exploration done
- [x] Define project goals: clear questions and hypotheses
- [x] Write README: first version of the project description

**Phase 2: Data analysis and development**

- [x] Data cleaning: handle missing values, outliers and inconsistent data
- [x] In-depth EDA: full exploratory data analysis with meaningful visualizations
- [x] First findings: key patterns and insights extracted
- [x] Documentation: progress and learnings documented continuously

**Phase 3: Finalization and presentation**

- [x] Finalize results: run final analyses
- [x] Create visualizations: meaningful charts for the presentation
- [ ] Complete documentation: revise README, code comments and project documentation
- [ ] Prepare presentation: develop storyline and create slides