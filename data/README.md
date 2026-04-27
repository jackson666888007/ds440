# Data folder

This folder stores external project data.

## Automatically downloaded by script

The analysis script downloads IMDb files automatically from:

https://developer.imdb.com/non-commercial-datasets/

Downloaded IMDb files are not included in this repository because they are large.

## Optional external revenue file

Place `box_office.csv` here to run revenue regression.

Supported format:

```csv
primaryTitle,startYear,revenue
Avatar,2009,2787965087
```

Alternative supported format:

```csv
tconst,revenue
tt0499549,2787965087
```

If this file is missing, the script still runs the IMDb baseline analysis.
