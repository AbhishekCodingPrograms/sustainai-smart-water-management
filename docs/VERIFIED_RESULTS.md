# Verified execution record

Author: Abhishek Maurya. Verification date: 27 October 2026 (Asia/Kolkata).

## Cloud compatibility update

The supplied Streamlit Cloud log uses Python 3.14.9 and attempts source builds of the original NumPy 2.2.6 and pandas 2.2.3 pins. The updated requirements use NumPy 2.3.3, pandas 2.3.3, Streamlit 1.52.2 and Altair 6.0.0. Scikit-learn remains 1.7.2. Upgrading only NumPy and pandas was insufficient: a real Python 3.14 test exposed Altair 5.5.0's `TypedDict(closed=True)` import error, so both UI packages were updated as well.

Updated environment: Windows, CPython **3.14.8**. Binary-only installation succeeded. **16 tests passed in 24.09 seconds**, including the Streamlit application smoke test. `evaluate.py` reproduced the exact threshold and synthetic confusion counts below. The test output is in `test-results-py314.txt`; current package versions are in the root `requirements-lock.txt`.

An independent pip dry-run with Linux x86-64 CPython 3.14 platform and ABI tags resolved all 42 runtime packages to wheels; no source build was required. A compact record is in `cloud-wheel-check.json`. This verifies package availability for the cloud platform, not live service health. An optional GitHub Actions matrix template is provided as `python-compatibility-workflow.example.yml`. It was not installed or executed because the available GitHub token does not permit publishing workflow files; the application fix does not require that permission.

Original Python 3.12 package versions and results are preserved below and in `requirements-original-py312.txt` for provenance. The primary PDF describes the original tested prototype. Its workflow and model behaviour are unchanged by this dependency compatibility update.

## Original submission environment and checks

Windows, CPython 3.12. Packages installed from PyPI into an isolated task directory; no user-wide environment changes. Core versions: NumPy 2.2.6, pandas 2.2.3, scikit-learn 1.7.2, Streamlit 1.50.0, Altair 5.5.0, pytest 8.4.2. Full versions are in requirements-lock.txt.

Final automated run: **16 passed in 44.21 seconds**. Command: `python -m pytest -q`. The execution environment needed a writable workspace TEMP/TMP and pytest basetemp because its default temporary directory was restricted. This was an environment adjustment, not a change in application behaviour.

Coverage includes deterministic generation; missing columns, duplicate times, NaN, negative values, gaps, infinity, naive timestamps and short input rejection; chronological sorting; label exclusion; past-only feature engineering; deterministic held-out threshold; critical rule activation; exact three-reading persistence; incident boundaries; invalid inspection transitions; persistent SQLite history; and Streamlit AppTest initial rendering, interaction and upload-mode empty-state handling. Full browser-based file upload and real hardware ingestion were not tested.

An initial test incorrectly expected the default fixture to cross an urgent-rule limit. The fixture does not do that. The assertion was corrected; urgent flow behaviour is tested independently with a 40 L/min input. Tests were rerun after the correction and a ticket-identity fix that includes the reference data. No scenario magnitude was changed to improve results.

## Synthetic holdout results

Reproduce with `python -m sustainai.data` followed by `python evaluate.py`. Generator seed 42; 2,880 total readings. A 1,920-reading reference supplies 1,344 training rows and 576 calibration rows. The later 960 readings are evaluation only. The score threshold is **0.5866461802335885** at the default 99th-percentile calibration quantile. Calibration exceedance is **5/576 (0.8681%)**.

| Reading-level outcome | AI flag | Actionable alert |
|---|---:|---:|
| True positive | 19 | 11 |
| False positive | 20 | 2 |
| False negative | 15 | 23 |
| True negative | 906 | 924 |

The truth labels identify any injected scenario, including a sensor-like pressure fault, rather than exclusively confirmed leaks. Alerts include both persistent model anomalies and independent critical rules. In this default fixture, no critical rule fires. The 13 alert readings form **2 inspection tickets**. Reading-level counts do not equal physical event counts or numbers of leaks.

| Injected scenario | Labelled readings | AI flags | Alert readings |
|---|---:|---:|---:|
| Simulated leak | 20 | 12 | 7 |
| Simulated burst | 6 | 6 | 4 |
| Simulated pressure fault | 8 | 1 | 0 |
| Normal | 926 | 20 | 2 |

Persistence reduces isolated false alerts but delays and suppresses detections. The pressure-fault scenario is missed by actionable alerting. This is a material prototype limitation, not evidence of safe operation. Explanations are robust feature comparisons and have not been validated as causal explanations. Normal-reference calibration is not enough to establish generalization.

## Document and delivery verification

The primary PDF is two pages and both rendered page images were visually inspected for clipping, overlap and readability. The workflow diagram is supplied as PNG and editable Mermaid. The editable workflow text is also included as Markdown. DOCX authoring was attempted, but the required rendering engine was unavailable; an unverified DOCX is not included. The assignment accepts PDF as a primary submission, so no slide deck is needed.

The application was also started on a local-only address and its dashboard, metrics, chart rendering and layout were inspected in the in-app browser. That review found browser-local timezone rendering under a UTC caption; chart scales and tooltips were corrected to explicitly use UTC, then the 16-test suite passed again. The temporary verification server is not a hosted deployment or a promise of an always-running preview.

The ZIP is checked for readable entries, required application/source/dataset/document files, and exclusion of caches, runtime databases, credentials and environment packages. SHA-256 checksums accompany the packaged files.

## Claims and remaining validation

This is a tested demo prototype. No production IoT deployment, field accuracy, hardware commissioning, measured water savings or financial return was verified. The local dashboard is intended for synthetic and de-identified data. Public hosting, authentication, tenant separation, durable cloud persistence, device freshness, penetration testing, notification delivery and safety-critical controls remain outside the implemented boundary.

Before a real pilot, obtain independently adjudicated field events and normal periods, verify sensor calibration, assess missed events and false tickets per zone-day, measure operator response time, review drift, and validate every maintenance action under site procedures. Impact claims require a defensible comparison and measured uncertainty.
