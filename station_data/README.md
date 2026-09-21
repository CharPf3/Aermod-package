# Surface station data

## Purpose

`surface_stations.csv` supports the coordinate search for nearby surface weather stations. Each row represents one WBAN station identifier.

The CSV contains:

- `wban`: five-digit WBAN station identifier
- `station_name`: station name shown to the user
- `state`: state or territory abbreviation
- `latitude`: station latitude in decimal degrees
- `longitude`: station longitude in decimal degrees

## Source

The station list and most coordinates were transcribed from the EPA document [Station Locations and 30-year Normals](https://www.epa.gov/sites/default/files/documents/STATION_LOCATIONS.PDF).

The PDF describes 237 climatological station locations but prints 241 WBAN identifiers because four entries pair stations together. This CSV keeps one row per WBAN so each identifier can be searched and checked for a requested year.

Coordinates are stored to the same two-decimal precision shown in the PDF, except for the documented Eureka entry below.

## Documented changes

Two coordinate decisions differ from the text printed in the PDF:

1. **Eureka, California (WBAN 24213):** The PDF lists Eureka as part of an Arcata/Eureka pair but does not print separate coordinates for Eureka. The CSV uses `40.81, -124.16`, rounded from the coordinates in [NOAA's ISD station history](https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv).
2. **Cedar City, Utah (WBAN 93129):** The PDF prints the longitude as positive `113.10`. The CSV uses `-113.10` because Cedar City is west of the prime meridian and NOAA's station history reports a negative longitude.

The following station-name cleanup does not change station identifiers or coordinates:

- Removed trailing pairing slashes from Arcata and Tallahassee.
- Combined the continued name `Wilkes-Barre/Scranton/Avoca` onto one line.
- Replaced curly apostrophes with plain apostrophes for consistent text encoding.

## Limitation

Inclusion in this CSV does not guarantee that a station has ISD-Lite data for every year. The download workflow must check NOAA's ISD-Lite directory for the requested year before presenting or downloading a file.

# Upper-air station data

## Source

`igra2-station-list.txt` is an unchanged copy of the NOAA [IGRA Version 2 station inventory](https://www.ncei.noaa.gov/data/integrated-global-radiosonde-archive/doc/igra2-station-list.txt) supplied for this project. The project copy was added on July 22, 2026, and no station values were edited.

Each fixed-width record contains an IGRA station identifier, latitude, longitude, elevation, optional U.S. state, station name, first year, last year, and observation count. Because station names contain spaces and some international records do not contain a state, the parser uses the documented column positions rather than splitting a line at every space.

The first and last years describe the station's overall period of record. They are useful for initial filtering but do not guarantee that every sounding is available during every date inside that period. The workflow must still verify the selected station archive and requested year.
