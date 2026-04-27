# DS440: Film Audience Preferences & Cultural Trends

This repository contains the code and supporting files for the DS440 final project.

## Project summary

This project studies how movie audience evaluation and market performance vary across genre and time, and whether time-aware star power adds explanatory value beyond core metadata.

The project keeps three signals separate:

- `averageRating` = perceived quality
- `numVotes` = popularity / audience attention
- `revenue` = market outcome

The analysis is organized around two branches:

1. **Baseline branch**: IMDb-only metadata and ratings.
2. **Extension branch**: box-office revenue and cast/star-power features layered on top of the baseline when coverage is available.

## Repository structure

```text
ds440/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   └── ds440_final_analysis.py
├── data/
│   ├── README.md
│   └── box_office.csv              # optional external revenue file
├── outputs/
│   ├── figures/                    # generated figures
│   └── tables/                     # generated tables
└── report/
    └── final report files, if included
```

## Data sources

### IMDb baseline data

The code downloads IMDb public non-commercial datasets automatically from:

https://developer.imdb.com/non-commercial-datasets/

Main files used:

- `title.basics.tsv.gz`
- `title.ratings.tsv.gz`

Optional cast/star-power files:

- `title.principals.tsv.gz`
- `name.basics.tsv.gz`

### Box office extension data

The optional revenue extension uses `data/box_office.csv`.

Expected format:

```csv
primaryTitle,startYear,revenue
Avatar,2009,2787965087
Pirates of the Caribbean: At World's End,2007,961000000
```

The script also supports this format:

```csv
tconst,revenue
tt0499549,2787965087
```

If `data/box_office.csv` is missing, the code still runs the IMDb baseline analysis and skips revenue regression.

## How to reproduce

### 1. Install packages

```bash
pip install -r requirements.txt
```

or:

```bash
pip install pandas numpy matplotlib scikit-learn requests
```

### 2. Run the analysis

```bash
python src/ds440_final_analysis.py
```

If you are using Jupyter or Google Colab, run:

```python
!python src/ds440_final_analysis.py
```

### 3. Check generated outputs

Figures will be saved to:

```text
outputs/figures/
```

Tables will be saved to:

```text
outputs/tables/
```

Expected baseline outputs include:

- `fig1_dataset_scale.png`
- `fig2_vote_distribution.png`
- `fig3_vote_concentration.png`
- `fig4_rating_by_genre_decade.png`
- `baseline_movie_table.csv`
- `high_vote_subset.csv`
- `dataset_scale.csv`
- `vote_concentration.csv`
- `avg_rating_by_genre_decade.csv`

If `box_office.csv` is available, additional outputs include:

- `revenue_matched_table.csv`
- `baseline_revenue_model_coefficients.csv`
- `baseline_revenue_model_metrics.csv`
- `fig5_key_coefficients.png`
- optional star-power ablation outputs

## Main analysis logic

1. Download IMDb baseline files.
2. Merge `title.basics` and `title.ratings` on `tconst`.
3. Filter to feature films with valid year, genre, runtime, rating, and vote count.
4. Create:
   - `decade`
   - `primaryGenre`
   - `logVotes`
5. Produce descriptive figures for:
   - dataset scale
   - vote distribution
   - vote concentration
   - rating by genre and decade
6. If box office data is available:
   - match revenue to IMDb movies by `tconst` or by `primaryTitle + startYear`
   - fit an interpretable log-revenue regression
   - attempt star-power feature construction and ablation

## Important interpretation note

The IMDb baseline branch is the most stable part of the project because it uses official IMDb identifiers and public IMDb datasets. The revenue extension depends on external box-office coverage and may use title-year matching, so revenue results should be interpreted as matched-subset results rather than full-population results.

## Team

- Beiwei Niu
- Jizhou Cheng
- Pinrui Chen
- Chengshun Zhao
- Harry Gu
