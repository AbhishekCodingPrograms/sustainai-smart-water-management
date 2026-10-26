# SustainAI — AI Enabled Smart Water Management and Leak Detection

**Abhishek Maurya · SustainAI Assignment 3B**

A runnable **demo prototype**, not a commissioned IoT installation. The app reviews historical readings, highlights unusual behaviour and gives a maintenance operator an evidence-based inspection queue. All bundled readings are synthetic. No live telemetry, external notifications, automatic valve control or real water savings are claimed.

## Start here

Use Python **3.12**. From this extracted project directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On macOS/Linux replace activation with `source .venv/bin/activate`. Open the local address printed by Streamlit. To install without shell activation, use `.venv\Scripts\python.exe` (Windows) or `.venv/bin/python` in place of `python`. Internet access is needed for initial package installation. No API keys are required.

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m sustainai.data --output data/demo.csv --seed 42
python evaluate.py
```

`requirements-lock.txt` records all dependency versions used in verification. For a closer environment reproduction, install it instead of the shorter requirements files. This lock was tested on Windows with Python 3.12; other operating systems were not tested.

## Five minute demonstration

1. Start in **Synthetic demo**. Read the historical date range and prototype notice.
2. Review flow, pressure and scores. Red markers denote alert readings, not confirmed leaks. Adjust the history window and inspect row evidence.
3. Open **Inspection workflow**, choose a ticket and save Acknowledged. Then record an inspection outcome and findings as Inspected; resolve after a verified repair or explanation. Inconclusive findings cannot close a ticket. Export the audit log.
4. Change the calibration quantile and observe alert counts. This changes the operating point, not the underlying model.
5. Try **Upload CSV** using `data/evaluation.csv`. Upload `data/reference.csv` as the trusted normal reference for the same demo operating regime. Errors are rejected with a clear message.

## Data contract

One meter/zone per file. CSV, UTF-8, at most 5 MB and 50,000 rows; at least 96 rows. Required columns:

| Column | Meaning | Accepted range |
|---|---|---|
| timestamp | ISO 8601 with `Z` or UTC offset | Unique, uninterrupted 15-minute intervals |
| flow_lpm | Average flow during the represented interval, L/min | 0–200 |
| pressure_bar | Pressure, bar | 0–16 |

Rows are sorted chronologically. Missing, nonfinite, duplicate and out-of-range data are rejected. Irregular intervals and gaps are rejected rather than imputed. Extra columns, including scenario labels, are discarded before modeling. Convert local timestamps and verify measurement units before uploading. UTC hour is used for daily patterns; train and evaluate under the same time convention. Fifteen-minute sampling cannot detect brief events reliably.

`demo.csv` has 2,880 readings: 30 days from 1 September 2026. Daily morning/evening demand plus seeded noise is supplemented with three injected scenarios. The first 1,920 readings contain no injected faults; the last 960 form the evaluation interval. This fixture is intentionally simpler than field conditions and does not capture all leak types, seasonality, holidays or sensor failures.

## Model and calibration

`sustainai/data.py` validates and generates data; `model.py` engineers seven features and handles scoring; `feedback.py` stores inspection events; `app.py` handles display and uploads. Tests exercise the pipeline and Streamlit app.

Features: flow, pressure, backward changes in both, trailing four-reading flow mean, sine and cosine of UTC hour. Features use present and earlier readings only. No scenario label or future reading enters the model. The trailing mean resets at the beginning of an evaluation file; its first three values use a shorter history.

Isolation Forest uses 200 trees, seed 42, one worker and `contamination='auto'`. The earlier 70% of the normal reference trains the forest, and the later 30% calibrates a threshold from the negative `score_samples` distribution. Higher scores mean more unusual. The default 99th-percentile threshold uses the `higher` quantile method; a strict `>` comparison flags readings. Scikit-learn's built-in contamination threshold is not used. No feature scaling is needed for these axis-aligned isolation trees.

Normal-reference calibration estimates an empirical exceedance rate only. It is not a leak probability, a future false-alarm guarantee, or field validation. Operators must verify that references describe normal operation, represent their site, and precede evaluation. Uploading evaluation data without a reference uses a synthetic baseline with a visible warning. Both train and calibration sets are presumed normal, not filtered by the AI.

Three consecutive model flags produce an **Inspect** alert (30 minutes from the first to the third reading). Pressure below 1.5 bar or flow above 20 L/min produces an immediate **Urgent** rule alert, independently of AI. These illustrative rule thresholds require site engineering approval. Contiguous alert readings become one ticket; interruptions can split a physical event. Explanations report the two largest absolute robust deviations from training medians using MAD scales; these are contextual comparisons, not causal attributions or a diagnosis. Daily patterns can make these comparisons imperfect.

## Inspection and feedback

Tickets progress New → Acknowledged → Inspected → Resolved, one step at a time. Inspection requires notes and a non-pending outcome. Outcomes include confirmed leak, legitimate usage, sensor fault and inconclusive. Resolution requires a conclusive outcome. The local append-only-by-application SQLite event log survives browser refresh; it is not a tamper-proof or authenticated audit system. Ticket IDs contain an evaluation-data hash and calibration quantile so changed inputs/settings do not overwrite a different investigation. The same ticket may have repeated same-state notes. Outcomes do **not** automatically retrain the model. An engineer should review evidence, create a versioned reference, recalibrate and compare a fixed holdout before release.

For a suspected leak, verify meter health and legitimate usage, inspect the pipe and isolate it only under approved maintenance procedures. Escalate urgent pressure loss through the site's normal incident process. The app sends no SMS/email and operates no equipment.

## Verification and impact

See `docs/VERIFIED_RESULTS.md` and `docs/demo_metrics.json` for the actual execution record and reproducible synthetic results. `evaluate.py` computes reading-level AI and alert confusion counts and scenario detection; labels are used only after scoring. Synthetic evaluation cannot establish field accuracy. No fabricated accuracy, water savings, currency savings or deployment claim appears in this submission.

For a real pilot, independently adjudicate alerts and random unflagged samples, track false tickets per zone-day and event recall, measure time to inspection, and estimate avoided loss using calibrated meters and a defensible counterfactual. Document uncertainty, occupancy changes and maintenance effects. Do not infer savings by multiplying anomalous flow by duration.

## Submission files and rubric

`Abhishek_Maurya_AIWorkflow.pdf` is the two-page primary submission; an editable Markdown version and standalone diagram accompany it. A verified DOCX export was unavailable because this environment has no document rendering engine. The complete source, tests, dataset, instructions and evidence are included in the ZIP.

| Evaluation criterion from assignment email | Evidence |
|---|---|
| Clarity of AI use case | Workflow page 1: unusual consumption/pressure as inspection support; `model.py` |
| Logical input-output mapping | Workflow page 1: units, features, scores, flags, tickets; data contract above |
| Strength of workflow design | Workflow page 2 diagram; validation, calibration, human inspection and reviewed feedback loop |
| Practical feasibility | Runnable Streamlit/scikit-learn build; tests, deployment and ESP32 guidance |
| Overall clarity | Two-page document, labeled synthetic demo, bounded claims and reproducible setup |

Assignment source: connected Gmail message “Assignment 3B: AI Enabled Solution Design | Submission Details - 26th October 2026”, received 26 October 2026. This package does not include private email bodies or account identifiers. The assignment permits a 1–2 page document **or** 3–4 slides; the document is supplied as the primary deliverable.

## References

- [scikit-learn IsolationForest API](https://scikit-learn.org/1.7/modules/generated/sklearn.ensemble.IsolationForest.html): algorithm and score orientation.
- [Streamlit deployment dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies).
- [Streamlit file organization](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization).

See `docs/DEPLOYMENT.md` and `docs/SECURITY_AND_IOT.md` before using anything beyond a local synthetic demonstration.
