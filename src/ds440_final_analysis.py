"""
DS440 Final Project - Reproducible Analysis Script

What this script creates:
1. IMDb baseline movie-level table
2. Descriptive figures for vote concentration and genre/decade patterns
3. Optional revenue baseline regression if box_office.csv is provided
4. Optional star-power ablation if cast data + revenue data are available
5. Tables and figures for the final report

How to run:
    pip install pandas numpy matplotlib scikit-learn requests
    python src/ds440_final_analysis.py

Core IMDb files are downloaded from:
    https://developer.imdb.com/non-commercial-datasets/

Optional local files:
    data/box_office.csv

Recommended box_office.csv columns:
    tconst,revenue

Alternative supported columns:
    primaryTitle,startYear,revenue

If you only run IMDb baseline, the script still creates the descriptive figures.
If you add box_office.csv, it also creates regression and ablation outputs.
"""

from pathlib import Path
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.linear_model import LinearRegression


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUT_DIR = PROJECT_ROOT / "outputs"
FIG_DIR = OUT_DIR / "figures"
TABLE_DIR = OUT_DIR / "tables"

for folder in [DATA_DIR, OUT_DIR, FIG_DIR, TABLE_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


IMDB_URLS = {
    "title.basics.tsv.gz": "https://datasets.imdbws.com/title.basics.tsv.gz",
    "title.ratings.tsv.gz": "https://datasets.imdbws.com/title.ratings.tsv.gz",
    "title.principals.tsv.gz": "https://datasets.imdbws.com/title.principals.tsv.gz",
    "name.basics.tsv.gz": "https://datasets.imdbws.com/name.basics.tsv.gz",
}


USE_SAMPLE = False
SAMPLE_NROWS = 500000


def download_file(url, path):
    if path.exists():
        print(f"Already exists: {path}")
        return

    print(f"Downloading {url}")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    print(f"Saved to {path}")


def read_imdb_tsv(filename, usecols=None, nrows=None):
    path = DATA_DIR / filename
    download_file(IMDB_URLS[filename], path)

    return pd.read_csv(
        path,
        sep="\t",
        usecols=usecols,
        nrows=nrows,
        na_values="\\N",
        low_memory=False,
        compression="gzip",
    )


def clean_money(x):
    if pd.isna(x):
        return np.nan
    s = str(x)
    s = s.replace("$", "").replace(",", "").replace("USD", "").strip()
    try:
        return float(s)
    except ValueError:
        return np.nan


def make_baseline_table():
    nrows = SAMPLE_NROWS if USE_SAMPLE else None

    basics = read_imdb_tsv(
        "title.basics.tsv.gz",
        usecols=["tconst", "titleType", "primaryTitle", "startYear", "runtimeMinutes", "genres"],
        nrows=nrows,
    )

    ratings = read_imdb_tsv(
        "title.ratings.tsv.gz",
        usecols=["tconst", "averageRating", "numVotes"],
        nrows=nrows,
    )

    basics["startYear"] = pd.to_numeric(basics["startYear"], errors="coerce")
    basics["runtimeMinutes"] = pd.to_numeric(basics["runtimeMinutes"], errors="coerce")
    ratings["averageRating"] = pd.to_numeric(ratings["averageRating"], errors="coerce")
    ratings["numVotes"] = pd.to_numeric(ratings["numVotes"], errors="coerce")

    joined = basics.merge(ratings, on="tconst", how="inner")

    movies = joined[
        (joined["titleType"] == "movie")
        & (joined["runtimeMinutes"] >= 60)
        & joined["startYear"].notna()
        & joined["genres"].notna()
        & joined["averageRating"].notna()
        & joined["numVotes"].notna()
    ].copy()

    movies["startYear"] = movies["startYear"].astype(int)
    movies["decade"] = (movies["startYear"] // 10) * 10
    movies["primaryGenre"] = movies["genres"].str.split(",").str[0]
    movies["logVotes"] = np.log10(movies["numVotes"].clip(lower=1))

    high_vote = movies[movies["numVotes"] >= 1000].copy()

    scale = pd.DataFrame(
        {
            "stage": [
                "IMDb title.basics",
                "IMDb title.ratings",
                "Joined basics + ratings",
                "Feature-film filtered baseline",
                "High-vote robustness subset",
            ],
            "count": [
                len(basics),
                len(ratings),
                len(joined),
                len(movies),
                len(high_vote),
            ],
        }
    )

    movies.to_csv(TABLE_DIR / "baseline_movie_table.csv", index=False)
    high_vote.to_csv(TABLE_DIR / "high_vote_subset.csv", index=False)
    scale.to_csv(TABLE_DIR / "dataset_scale.csv", index=False)

    return movies, high_vote, scale


def plot_dataset_scale(scale):
    plt.figure(figsize=(8, 4))
    plt.bar(scale["stage"], scale["count"])
    plt.xticks(rotation=30, ha="right")
    plt.ylabel("Number of titles")
    plt.title("Dataset Scale Across Main Filtering Steps")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig1_dataset_scale.png", dpi=200)
    plt.close()


def plot_vote_distribution(movies):
    plt.figure(figsize=(7, 4))
    plt.hist(np.log10(movies["numVotes"].clip(lower=1)), bins=50)
    plt.xlabel("log10(number of IMDb votes)")
    plt.ylabel("Number of movies")
    plt.title("Vote Counts Are Strongly Right-Skewed")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig2_vote_distribution.png", dpi=200)
    plt.close()


def plot_vote_concentration(movies):
    sorted_votes = movies["numVotes"].sort_values(ascending=False).reset_index(drop=True)
    cutoff = max(1, int(len(sorted_votes) * 0.10))
    top_votes = sorted_votes.iloc[:cutoff].sum()
    rest_votes = sorted_votes.iloc[cutoff:].sum()

    shares = pd.DataFrame(
        {
            "group": ["Top 10% titles", "Bottom 90% titles"],
            "vote_share": [top_votes / (top_votes + rest_votes), rest_votes / (top_votes + rest_votes)],
        }
    )
    shares.to_csv(TABLE_DIR / "vote_concentration.csv", index=False)

    plt.figure(figsize=(5, 4))
    plt.bar(shares["group"], shares["vote_share"])
    plt.ylabel("Share of all votes")
    plt.title("Vote Attention Is Concentrated")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig3_vote_concentration.png", dpi=200)
    plt.close()


def plot_rating_by_genre_decade(movies):
    top_genres = movies["primaryGenre"].value_counts().head(8).index.tolist()
    temp = movies[movies["primaryGenre"].isin(top_genres)].copy()
    temp = temp[(temp["decade"] >= 1950) & (temp["decade"] <= 2020)]

    pivot = temp.pivot_table(
        index="primaryGenre",
        columns="decade",
        values="averageRating",
        aggfunc="mean",
    )

    pivot.to_csv(TABLE_DIR / "avg_rating_by_genre_decade.csv")

    plt.figure(figsize=(9, 4.5))
    plt.imshow(pivot, aspect="auto")
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45)
    plt.yticks(range(len(pivot.index)), pivot.index)
    plt.colorbar(label="Average IMDb rating")
    plt.title("Average Rating by Genre and Decade")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig4_rating_by_genre_decade.png", dpi=200)
    plt.close()


def load_box_office(movies):
    path = DATA_DIR / "box_office.csv"
    if not path.exists():
        print("No data/box_office.csv found. Skipping revenue regression.")
        return None

    box = pd.read_csv(path)
    box.columns = [c.strip() for c in box.columns]

    if "revenue" not in box.columns:
        raise ValueError("box_office.csv must contain a revenue column.")

    box["revenue"] = box["revenue"].apply(clean_money)
    box = box[box["revenue"].notna() & (box["revenue"] > 0)].copy()
    box["logRevenue"] = np.log10(box["revenue"])

    if "tconst" in box.columns:
        model_df = movies.merge(box[["tconst", "revenue", "logRevenue"]], on="tconst", how="inner")
    elif {"primaryTitle", "startYear"}.issubset(box.columns):
        box["startYear"] = pd.to_numeric(box["startYear"], errors="coerce").astype("Int64")
        model_df = movies.merge(
            box[["primaryTitle", "startYear", "revenue", "logRevenue"]],
            on=["primaryTitle", "startYear"],
            how="inner",
        )
    else:
        raise ValueError("box_office.csv needs either tconst or primaryTitle + startYear.")

    model_df.to_csv(TABLE_DIR / "revenue_matched_table.csv", index=False)
    return model_df


def prepare_model_matrix(df, include_star=False):
    work = df.copy()

    features = ["logVotes", "averageRating", "runtimeMinutes", "decade", "primaryGenre"]
    if include_star and "star_power_max" in work.columns:
        features.append("star_power_max")
    if include_star and "star_power_top3" in work.columns:
        features.append("star_power_top3")

    work = work.dropna(subset=features + ["logRevenue"]).copy()

    X = pd.get_dummies(work[features], columns=["primaryGenre"], drop_first=True)
    y = work["logRevenue"]
    return X, y, work


def run_regression(model_df, include_star=False, label="baseline"):
    X, y, used = prepare_model_matrix(model_df, include_star=include_star)

    if len(used) < 50:
        print(f"Not enough rows for {label} regression. Rows: {len(used)}")
        return None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    r2 = r2_score(y_test, pred)
    rmse = mean_squared_error(y_test, pred) ** 0.5

    coef = pd.DataFrame(
        {
            "feature": X.columns,
            "coefficient": model.coef_,
        }
    ).sort_values("coefficient", key=lambda s: s.abs(), ascending=False)

    metrics = pd.DataFrame(
        {
            "model": [label],
            "n_rows": [len(used)],
            "r2_test": [r2],
            "rmse_test_log10": [rmse],
        }
    )

    coef.to_csv(TABLE_DIR / f"{label}_coefficients.csv", index=False)
    metrics.to_csv(TABLE_DIR / f"{label}_metrics.csv", index=False)

    return metrics, coef


def plot_key_coefficients(coef):
    keep = coef[coef["feature"].isin(["logVotes", "averageRating", "runtimeMinutes", "decade"])].copy()
    if keep.empty:
        return

    plt.figure(figsize=(6, 4))
    plt.bar(keep["feature"], keep["coefficient"])
    plt.ylabel("Linear regression coefficient")
    plt.title("Key Coefficients in Log-Revenue Baseline")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig5_key_coefficients.png", dpi=200)
    plt.close()


def build_star_power_from_imdb(model_df):
    print("Attempting to build star-power features from IMDb principals.")
    nrows = SAMPLE_NROWS if USE_SAMPLE else None

    principals = read_imdb_tsv(
        "title.principals.tsv.gz",
        usecols=["tconst", "ordering", "nconst", "category"],
        nrows=nrows,
    )

    principals = principals[principals["category"].isin(["actor", "actress"])].copy()
    principals["ordering"] = pd.to_numeric(principals["ordering"], errors="coerce")
    principals = principals[principals["ordering"] <= 10].copy()

    actor_movies = principals.merge(
        model_df[["tconst", "startYear", "logRevenue"]],
        on="tconst",
        how="inner",
    )
    actor_movies = actor_movies.dropna(subset=["nconst", "startYear", "logRevenue"]).copy()
    actor_movies = actor_movies.sort_values(["nconst", "startYear"])

    actor_movies["prior_actor_score"] = (
        actor_movies
        .groupby("nconst")["logRevenue"]
        .transform(lambda s: s.shift().expanding().mean())
    )

    actor_movies = actor_movies.dropna(subset=["prior_actor_score"]).copy()

    star = (
        actor_movies
        .groupby("tconst")["prior_actor_score"]
        .agg(
            star_power_max="max",
            star_power_top3=lambda s: s.sort_values(ascending=False).head(3).sum(),
        )
        .reset_index()
    )

    star.to_csv(TABLE_DIR / "star_power_features.csv", index=False)
    return star


def run_optional_revenue_and_star_analysis(movies):
    model_df = load_box_office(movies)
    if model_df is None:
        return

    baseline_result = run_regression(model_df, include_star=False, label="baseline_revenue_model")
    if baseline_result is not None:
        metrics, coef = baseline_result
        plot_key_coefficients(coef)

    star_path = TABLE_DIR / "star_power_features.csv"
    if star_path.exists():
        star = pd.read_csv(star_path)
    else:
        star = build_star_power_from_imdb(model_df)

    model_star = model_df.merge(star, on="tconst", how="left")
    star_result = run_regression(model_star, include_star=True, label="baseline_plus_star_power")

    if baseline_result is not None and star_result is not None:
        all_metrics = pd.concat([baseline_result[0], star_result[0]], ignore_index=True)
        all_metrics.to_csv(TABLE_DIR / "model_comparison.csv", index=False)

        plt.figure(figsize=(5, 4))
        plt.bar(all_metrics["model"], all_metrics["r2_test"])
        plt.ylabel("Test R-squared")
        plt.title("Baseline vs. Baseline + Star Power")
        plt.xticks(rotation=15, ha="right")
        plt.tight_layout()
        plt.savefig(FIG_DIR / "fig6_ablation_r2.png", dpi=200)
        plt.close()


def main():
    movies, high_vote, scale = make_baseline_table()

    plot_dataset_scale(scale)
    plot_vote_distribution(movies)
    plot_vote_concentration(movies)
    plot_rating_by_genre_decade(movies)

    run_optional_revenue_and_star_analysis(movies)

    print("\nDone.")
    print(f"Figures saved to: {FIG_DIR}")
    print(f"Tables saved to: {TABLE_DIR}")


if __name__ == "__main__":
    main()
