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

## Hypotheses

| | Hypothesis | Q |
| --- | --- | --- |
| H1 | Top hours concentrate at a few stations, not spread across Berlin | 1 |
| H2 | Both pollutants highest in winter, lowest in summer, at all stations | 2 |
| H3 | The same few stations have the most hours above the reference levels, both pollutants | 3 |

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

## How to run

    uv sync
    uv run python fetch.py        # only if raw/ is empty
    # then run notebooks 01 → 04 in order

## Stack

Python 3.14 · uv · pandas · numpy · matplotlib · seaborn

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