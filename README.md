# Air Quality Project

## Project

Berlin air pollution, 2025: when and where are people exposed most?

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
Sampling height: ~3.5–4 m above container roof

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

|  | Period | EU 2030 | Allowed/year | WHO | Allowed/year |
| --- | --- | --- | --- | --- | --- |
| NO₂ | 1 hour | 200 | 3 | – | – |
| NO₂ | 24 hours | 50 | 18 | 25 | 3–4 days (99th percentile) |
| NO₂ | year | 20 | – | 10 | – |
| PM2.5 | 24 hours | 25 | 18 | 15 | 3–4 days (99th percentile) |
| PM2.5 | year | 10 | – | 5 | – |

Sources: [Directive (EU) 2024/2881, Annex I, Table 1](https://eur-lex.europa.eu/eli/dir/2024/2881/oj) · [WHO guidelines 2021](https://www.who.int/publications/i/item/9789240034228)

## Analyses

|  | Compute | Note | Q |
| --- | --- | --- | --- |
| 1 | Top 10% station-hours across all stations, per pollutant | Hour-of-day mean per station × hour; not single maximum | 1 |
| 2 | Count of top station-hours per station | Which stations dominate | 1, 3 |
| 3 | Seasonal mean per station | Seasons: Dec–Feb, Mar–May, Jun–Aug, Sep–Nov | 2 |
| 4 | Hours above reference levels per station; days above 24-hour levels vs. allowed | Hours: indicator of extreme exposure (hourly value vs. 24-hour level); only NO₂ 200 is a true hourly limit. Days: compliance check | 3 |
| 5 | Top station-hours as multiple of the annual level | Scale only, not an exceedance | 3 |

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
    - top station-hours ÷ annual level
- Valid-hour coverage reported per aggregate

## Notebooks

| 01_data | Load, time zone, drops, outliers, coverage, hourly PM2.5 availability |
| 02_peak_hours | Top 10% station-hours and count per station, NO₂ and PM2.5 |
| 03_season | Seasonal means per station, NO₂ and PM2.5 |
| 04_reference_levels | Hours above reference levels per station; days vs. allowed; top hours as multiple of annual level |

## How to run

    uv sync
    uv run python fetch.py        # only if raw/ is empty
    # then run notebooks 01 → 04 in order

## Stack

python · pandas · matplotlib · seaborn

## Status

**Phase 1 Setup and project planning**

- [x] Select dataset: suitable dataset found, first exploration done
- [x] Define project goals: clear questions and hypotheses
- [x] Write README: first version of the project description

**Phase 2 Data analysis and development**

- [ ] Data cleaning: handle missing values, outliers and inconsistent data
- [ ] In-depth EDA: full exploratory data analysis with meaningful visualizations
- [ ] First findings: key patterns and insights extracted
- [ ] Documentation: progress and learnings documented continuously

**Phase 3 Finalization and presentation**

- [ ] Finalize results: run final analyses
- [ ] Create visualizations: meaningful charts for the presentation
- [ ] Complete documentation: revise README, code comments and project documentation
- [ ] Prepare presentation: develop storyline and create slides