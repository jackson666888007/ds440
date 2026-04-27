# DS440: Film Audience Preferences & Cultural Trends

**Final Project Report**  
Beiwei Niu · Jizhou Cheng · Pinrui Chen · Chengshun Zhao · Harry Gu  
Data Sciences Capstone Course · Spring 2026

## Abstract

DS440 is a movie analytics project about audience evaluation, public attention, market outcomes, and time-aware star power. The project asks how movie ratings, vote counts, and box-office revenue vary across genre and era, and whether cast history adds explanatory value after core metadata are already controlled. We intentionally keep three signals separate: average rating as perceived quality, vote count as popularity, and revenue as market outcome. The final product is a modular movie-level analysis pipeline with a guaranteed IMDb-only baseline branch and an additive extension branch for box-office and cast information. The pipeline is organized around four milestones: a stable baseline table, descriptive analysis of audience attention, an interpretable log-revenue baseline, and a time-aware star-power extension tested through ablation. Our results show that audience attention is highly concentrated, that vote count is the strongest signal in the current revenue baseline, and that time-aware star-power features add modest but meaningful incremental predictive value. We report these results carefully because revenue coverage is uneven and star effects can be selection-biased. The final contribution is not only a model; it is a transparent, defensible workflow that separates quality, popularity, and market success while leaving room for future refinement.

**Keywords:** IMDb; movie analytics; audience ratings; box office; star power; interpretable regression; ablation

---

## 1. Introduction and Research Motivation

Movie success is not a single outcome. A film can be highly rated but not widely watched, widely watched but not highly rated, or commercially successful for reasons that are not fully captured by audience ratings. This project starts from that tension. DS440 studies how audience evaluation and market performance vary across genre and era, and whether time-aware star power adds useful information beyond core metadata.

The project keeps three signals separate from the beginning. Average rating is treated as a signal of perceived quality. Vote count is treated as a signal of popularity and public attention. Box-office revenue is treated as a market outcome. These variables are related, but they are not interchangeable. Treating them as the same would hide the difference between a movie that a small group loves and a movie that becomes broadly visible in the market.

The central research question is: after controlling for genre, decade, rating, and votes, does cast history still help explain revenue? This question connects the descriptive part of the project to the modeling part. First, we describe how ratings and votes behave across the movie landscape. Then we build a transparent revenue baseline. Finally, we test whether time-aware star-power features add incremental signal on top of that baseline.

The project is intentionally designed to be interpretable rather than unnecessarily complex. A simple model is useful here because it lets us explain what each variable contributes before adding more advanced methods. This matches the course goal: move from a real-world question to data and design decisions, then to a working model, and finally to results that can be communicated clearly to readers.

---

## 2. Background and Prior Work

Prior work supports the project but also warns against simple interpretations. IMDb ratings are often used as if they were direct measures of audience quality, but IMDb explains that its displayed score is a weighted average rather than a plain arithmetic mean [1]. That does not make ratings useless. It means ratings should be handled carefully, especially when comparing titles across different eras and attention levels.

A second lesson from prior work is that attention in online rating systems is highly uneven. Ramos et al. show that movie-rating behavior has strong statistical regularities and heavy-tailed attention patterns [2]. This matters because many titles receive only limited engagement, while a smaller group receives a large share of votes. Because of this, vote count is not just background noise; it is an important variable that captures popularity.

Research connecting IMDb voting data to movie economics also shows that ratings, votes, budget, and box office are related but not identical [3]. This supports our decision to keep audience evaluation and market outcome separate. Prior work on motion picture profits further shows that revenue is highly uncertain and dominated by heavy tails and superstar effects [4]. This means revenue should be modeled on a logarithmic scale and interpreted with caution.

The star-power literature is mixed. Some studies find that stars can contribute to commercial success, while others emphasize that star estimates are vulnerable to selection bias because famous actors do not choose movies randomly [5]. Therefore, our project does not claim that stars directly cause revenue. Instead, we test whether time-aware star-power features add incremental predictive value after the baseline variables are already included.

---

## 3. Data and Project Design

The final report is organized around four milestones, which also match the way the project was developed over the semester. This milestone structure keeps the project readable and shows how the work progressed from data construction to interpretation.

| Milestone | Purpose | Main output | Why it matters |
|---|---|---|---|
| M1 | Baseline data | Movie-level IMDb table | Guarantees a coherent deliverable |
| M2 | Descriptive analysis | Rating/vote patterns | Separates quality from popularity |
| M3 | Revenue baseline | Interpretable OLS model | Explains market outcome transparently |
| M4 | Star-power extension | Baseline-vs-stars ablation | Tests incremental cast signal |

**M1: Baseline movie-level table.** The baseline branch starts with IMDb `title.basics` and `title.ratings`, merged on `tconst`. It filters to feature films with usable year, genre, runtime, rating, and vote-count fields. This branch is the minimum guaranteed deliverable because it can support a complete descriptive analysis even if later external joins are thin.

**M2: Descriptive analysis.** The descriptive branch compares rating and vote-count patterns by genre and decade. This milestone addresses whether popularity and perceived quality move together or diverge. It also provides the first evidence about how uneven audience attention is.

**M3: Interpretable revenue baseline.** The baseline model predicts log revenue using genre indicators, decade, average rating, log-transformed votes, and runtime when available. We use log revenue because film revenue is strongly skewed and because prior work treats movie profits as heavy-tailed [4].

**M4: Time-aware star-power extension.** The extension branch adds box-office and cast information only after the baseline branch is stable. Star power is built from pre-release information: each actor receives a prior-performance score based on earlier films, and movie-level features are formed using aggregates such as the maximum actor score or top-three sum. This avoids data leakage.

**Figure 1.** DS440 uses a guaranteed IMDb baseline branch and an additive extension branch for revenue and cast features.

---

## 4. Model and System Development

The system development process followed the same four milestones. In M1, the team built a stable movie-level baseline table. This step mattered because later modeling depends on a clean unit of analysis. The final pipeline does not treat all raw movie records as equal. It restricts the working set to feature films with usable metadata and then tracks the effect of each filter.

In M2, the team examined the vote distribution and rating patterns. This was not just exploratory decoration. It shaped later decisions. Because votes are highly skewed, the pipeline maintains both a full working subset and a higher-signal robustness subset. This lets the team ask whether conclusions depend on many low-attention titles or whether they remain visible among titles with stronger audience signal.

In M3, the first interpretable revenue model was specified and run on the revenue-matched subset. The model is linear in the covariates and predicts log revenue. This choice is deliberate: a linear baseline is easier to explain, easier to diagnose, and useful as a starting point before adding the star-power extension. The model is not presented as the most complex possible predictor; it is presented as a transparent baseline.

In M4, the time-aware star-power prototype was validated. The important system contribution is the actor-history path: movie to cast, cast to prior actor history, and actor history to movie-level feature. The feature is time-aware because it uses only films released before the focal movie. This protects the design from using future information and makes the feature closer to what would have been knowable at the time of release.

| Stage | Approx. scale | Role in analysis |
|---|---:|---|
| IMDb title.basics | 11.2M records | Raw title metadata |
| IMDb title.ratings | 1.55M records | Raw rating/vote source |
| Baseline feature-film subset | 312,400 titles | Main M1/M2 working set |
| High-vote robustness subset | 48,700 titles | Checks sparse-vote noise |
| Revenue-matched subset | 2,840 titles | M3/M4 modeling subset |

**Figure 2.** Dataset scale and sample shrinkage across the baseline and extension branches. Log scale is used because the raw inputs are much larger than the matched modeling subset.

---

## 5. Experiments and Results

**M2 result: audience attention is highly concentrated.** The first descriptive result is that audience attention is not evenly spread across movies. Vote counts are strongly right-skewed: many movies have low engagement, while a smaller group receives most public attention. This supports the decision to analyze popularity separately from rating. It also supports the use of a robustness subset, because low-vote titles may have unstable ratings.

**Figure 3.** A small top-decile group of titles holds most of the vote share, showing why popularity and perceived quality must be separated.

**M3 result: the interpretable revenue baseline is operational.** The first revenue model behaves in a stable and interpretable way on the matched subset. Vote count emerges as the dominant explanatory signal, while rating adds a smaller positive contribution. This result is reasonable because a film that attracts more public attention is also more likely to have commercial visibility. The model does not prove causality, but it gives a clear baseline for understanding market outcome.

**Figure 4.** Stage-1 coefficient comparison shows that log-transformed vote count is the dominant signal in the current revenue baseline.

**M4 result: time-aware star power adds incremental signal.** When the time-aware star-power features are added to the baseline model, the model fit improves modestly. This is an important result because it shows that cast history contributes information beyond genre, decade, rating, votes, and runtime. However, the interpretation is intentionally cautious. We report this as incremental predictive value, not as proof that stars cause revenue to increase.

**Figure 5.** The first ablation suggests modest incremental explanatory value from time-aware star-power features.

**Interpretation.** Together, the experiments show that the project moved beyond prototype-level framing. The final analysis now has a stable baseline table, first descriptive results, a working revenue baseline, and a feasible star-power extension. The results are informative but still bounded by coverage and selection limitations. This is why the report presents them as a careful final project analysis rather than as a claim of causal discovery.

---

## 6. Final Product and Deliverables

The final deliverable is not just a single regression model. It is a modular movie-analytics pipeline that can be explained, reused, and extended. The pipeline produces a clean movie-level dataset, descriptive figures about rating and vote behavior, an interpretable revenue model, and a time-aware star-power ablation framework.

The product also includes a reporting structure. Each milestone has a role: M1 establishes the baseline data, M2 explains audience attention, M3 connects audience signals to market outcome, and M4 tests whether cast history adds additional information. This structure is useful because it lets the reader understand the project even if some extension joins remain incomplete.

The main message delivered to readers is that movie outcomes should not be reduced to one score. Rating, popularity, and revenue capture different dimensions of movie success. A strong data-science design should keep them separate, model them transparently, and avoid over-claiming what the model can prove.

| Deliverable | What it contains | Message to reader |
|---|---|---|
| Baseline dataset | IMDb movie-level table | Coherent analysis can stand without external joins |
| EDA figures | Genre/decade rating and vote patterns | Popularity and quality should be separated |
| Revenue baseline | Interpretable log-revenue OLS | Simple variables already explain meaningful signal |
| Star-power ablation | Baseline vs. baseline+stars | Cast history adds incremental, non-causal signal |

---

## 7. Limitations, Lessons Learned, and Future Work

The largest limitation is join coverage. The IMDb baseline branch is large and stable, but box-office and cast data are only available for a smaller matched subset. Coverage is also uneven across eras and production contexts. Older films and non-U.S. titles may be under-represented. Therefore, the matched subset should not be treated as a perfect representation of all movies.

A second limitation is sparse-vote noise. Many titles have very few votes, which means their ratings may not be reliable measures of perceived quality. The high-vote robustness subset helps address this problem, but it also changes the population being studied. A strong final interpretation must be clear about which results come from the full set and which come from the higher-signal subset.

A third limitation is causal interpretation. Even if star-power features improve model fit, the result does not prove that famous actors directly cause more revenue. Stars choose projects non-randomly, and high-budget projects may attract stars before release. For that reason, the final report frames star power as incremental predictive value rather than causal impact.

The main lesson learned is that data-science projects are strongest when the design is resilient. Separating the guaranteed baseline branch from the additive extension branch prevented the whole project from depending on difficult external joins. This made the analysis more robust and allowed the team to move from framing to results without redesigning the project.

Future work should expand and audit the revenue and cast joins, add stronger confidence interval reporting for the baseline model, test alternative models after the interpretable baseline is fully understood, and improve visual analytics for genre-by-decade trends. A future version could also compare different star-power definitions and test whether the effect is stronger in specific genres or release eras.

---

## 8. Additional Analysis and Reader Guidance

The figures and tables in this report should be read together rather than separately. The dataset scale figure explains why the project cannot rely only on the revenue-matched subset: it is useful for modeling, but it is much smaller than the baseline IMDb branch. The vote-share figure explains why raw rating comparisons need caution: titles with very low attention may produce unstable average ratings. The ablation figure then shows how the star-power extension should be interpreted: it adds signal, but only after the baseline is already understood.

For readers, the main practical takeaway is that a movie analytics project should begin with a guaranteed and interpretable baseline. This avoids a common project failure where an ambitious external-data join becomes the entire project. In DS440, the baseline branch can answer descriptive questions about quality and popularity even if box-office or cast joins are incomplete. The extension branch then adds extra value without controlling the entire success of the project.

The project also shows why model simplicity can be an advantage. A more complex model might improve prediction, but it would make it harder to explain why a result occurs. Because this is a final capstone report, interpretability matters. The goal is to produce not only a score, but also an explanation that a reader can understand: audience attention is uneven, popularity matters strongly for revenue, and cast history provides additional but limited information.

---

## 9. Team Workflow and Final Integration

The final version of the project also reflects a workflow lesson. Earlier assignments focused on framing, prior work, and initial approach. The later assignments required the team to transform that framing into a working system with milestones, first outputs, and limitations. Using M1 through M4 as a common structure helped the written report, slides, and oral presentation stay aligned.

The team also learned that final reporting is not only about adding results. It is about making sure the reader can follow the connection from question to data, from data to model, from model to result, and from result to limitation. The final report therefore emphasizes not only what the model shows, but also what it cannot show. This is especially important for the star-power feature, because it would be easy to overstate its meaning without careful interpretation.

This structure is designed to be useful after the class as well. A future user could update the revenue join, expand the cast table, try a different model, or define star power in another way while still using the same baseline/extension framework. In that sense, the final product is both an analysis and a reusable project design.

---

## 10. Conclusion

DS440 shows that a movie-level data-science project can separate perceived quality, public attention, and market outcome while testing whether cast history adds useful information. The project began as a framing problem, but by the final report it had become a working analysis pipeline with clear data construction, interpretable modeling, and a defensible extension.

The final answer is careful rather than exaggerated. Audience attention is highly concentrated. Popularity is strongly connected to revenue in the current model. Time-aware star-power features add modest signal beyond the baseline. But the matched subset is limited, and the results should not be read as causal proof. The value of the project is that it makes these distinctions explicit and gives the reader a transparent way to understand movie success through data.

---

## References

[1] IMDb Help Center. Weighted Average Ratings. https://help.imdb.com/article/imdb/track-movies-tv/weighted-average-ratings/

[2] Ramos, M., Calvao, A. M., and Anteneodo, C. 2015. Statistical patterns in movie rating behavior. PLOS ONE 10, 8, e0136083.

[3] Wasserman, M., Mukherjee, S., Scott, K., Zeng, X. H. T., Radicchi, F., and Amaral, L. A. N. 2015. Correlations between user voting data, budget, and box office for films in the Internet Movie Database. Journal of the Association for Information Science and Technology 66, 4, 858-868.

[4] De Vany, A. S. and Walls, W. D. 2004. Motion picture profit, the stable Paretian hypothesis, and the curse of the superstar. Journal of Economic Dynamics and Control 28, 6, 1035-1057.

[5] Hofmann, J., Clement, M., Volckner, F., and Hennig-Thurau, T. 2017. Empirical generalizations on the impact of stars on the economic success of movies. International Journal of Research in Marketing 34, 2, 442-461.

[6] Li, D. and Liu, Z.-P. 2022. Predicting box-office markets with machine learning methods. Entropy 24, 5, 711.
