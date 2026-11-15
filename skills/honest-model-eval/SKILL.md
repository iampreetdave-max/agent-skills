---
name: honest-model-eval
description: Keep a machine-learning model honest from the first look at the data to the final number. Audits the dataset before any modelling (size, balance, duplicates, quality, what each column really means), enforces a prediction-time contract so no feature from the future leaks in (pre-match models especially), splits by time, compares against baselines and the market, and reports calibrated results with their uncertainty. Use when building, reviewing or debugging any predictive model, especially forecasting, sports, finance, churn or anything with time in it, and whenever results look too good.
---

# Honest model evaluation

Vibe-coded models leak. The agent finds a column that predicts the target, uses it, reports 92% accuracy, and the model collapses in production because that column does not exist yet when the prediction is made. This skill stops that.

## The rule: never assume anything

Not the meaning of a column, not that the data is clean, not that a feature exists when the prediction is made, not that the split is fair. Write every assumption down and confirm it with the user or the data source's docs.

## Step 1: Audit the data before any modelling

```
python <this-skill-dir>/scripts/audit.py data.csv --target <column> [--time <column>]
```

It reads CSV or Parquet and reports rows and columns, types, missing values, duplicate rows, constant and ID-like columns, the target's balance, the time range, and leak suspects: columns that almost determine the target on their own, or whose names suggest post-event data.

Then tell the user plainly:

- **How big it is**, and whether that is enough for what they want. A few hundred rows is a toy; say so.
- **Whether the target is balanced.** If it is not, accuracy is meaningless: use PR-AUC, recall at a fixed precision, or balanced metrics, and say which.
- **Whether the data is good, weak or trash**, with the reason. "This dataset cannot support this model" is a valid and useful result.
- **A column dictionary:** each column, what you think it means, and VERIFIED or ASSUMED. Ask the user to confirm every ASSUMED one before training. Names lie: `home_score` may be the final score, `odds` may be the closing line, `balance` may be after the transaction.

## Step 2: The prediction-time contract

Write down exactly when a prediction is made, for example "pre-match, two hours before kickoff" or "the moment a loan application is submitted". Then, for every feature:

- **Is it known at that moment?** Final scores, closing odds, post-match stats, month-end balances and anything computed after the event are not.
- **Aggregates** (season averages, rolling form) must use only events strictly before this one, never the event itself.
- **Back-filled or corrected sources:** if the provider fixed historical values later, your history is cleaner than what production will see.
- **For a pre-match model**, confirm that each feature can actually be fetched pre-match from a real source before building anything. Do this first, not after the model scores well.

Drop or rebuild every feature that fails.

## Step 3: Split like production

- **Anything with time:** split by time. Train on the past and test on the future, ideally walk-forward with rolling or expanding windows. Never a random split.
- **Same entity on both sides** (one match seen from both teams, one customer, near-duplicate rows): group them so they cannot straddle the split.
- Fit scalers, encoders, imputers and target encoders on the training fold only, inside the pipeline.
- Keep one final holdout untouched until the end, and look at it once.

## Step 4: Baselines first

Before the model, score the simple answers: majority class, last value, home team wins, and the market. For sports and betting, the market's implied probability with the bookmaker margin removed is the baseline to beat. Beating raw accuracy means little; beating the closing line is the real test. A model that does not beat a baseline is not a model yet.

## Step 5: Results that look too good are a bug

Treat each of these as a leak until proven otherwise:

- accuracy far above the market, or above published results for the problem
- one feature carrying most of the importance
- a big gap between random-split validation and the time-split test
- performance that drops sharply on the newest data

## Step 6: Report honestly

- Metrics on the time-split test set, with the sample size and a bootstrap confidence interval.
- **Calibration:** a reliability curve plus Brier score or log loss. When the model says 70%, it should be right about 70% of the time.
- **Betting-style outputs:** ROI with its confidence interval, the number of bets, and closing-line value.
- What was dropped for leakage, what is still ASSUMED, and what would change the conclusion.
- Write "the data does not support this model" when that is the truth.
