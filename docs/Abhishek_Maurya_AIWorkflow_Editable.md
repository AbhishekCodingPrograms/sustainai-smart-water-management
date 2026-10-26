Smart Water Management and Leak Detection

SustainAI Assignment 3B  |  Abhishek Maurya  |  AI Workflow

Problem and solution context

Unnoticed leaks and abnormal demand can delay maintenance in buildings and small campuses. SustainAI reviews a single water zone and prioritizes unusual flow or pressure for human inspection. Its purpose is earlier investigation; it does not establish that an anomaly is a leak. The delivered Streamlit application is a tested historical demo prototype, not a deployed production IoT system.

AI use case and choice

AI sits between validated sensor history and the maintenance queue. Isolation Forest performs multivariate anomaly detection because confirmed leak labels are often scarce and unusual combinations of flow, pressure and time may be missed by a single fixed limit. The forest isolates uncommon observations; separate engineering rules retain transparent urgent triggers. Legitimate high demand and sensor faults can also appear unusual.

Specific inputs and outputs

Input: one zone of continuous 15-minute CSV readings with timezone-aware timestamp, average flow in litres per minute and pressure in bar. Reject missing values, duplicates, gaps, nonfinite values and readings outside 0–200 L/min or 0–16 bar. Extra fields and synthetic scenario labels never enter the model.

Processing: sort by time; calculate backward flow and pressure changes, a trailing four-reading flow mean and sine/cosine of UTC hour. Together with flow and pressure these form seven features. Current and earlier readings only are used. Training uses the earlier 70% of a verified normal reference; a later 30% calibrates the threshold. Evaluation readings are separate.

Output: a negative Isolation Forest score_samples value (higher means more unusual), threshold flag, two contextual deviations from training medians, and an inspection severity. The default threshold is the 99th percentile of held-out normal scores. It is an empirical operating point, not a probability or a guaranteed false-alarm rate.

Decision and human responsibility

Three consecutive model flags trigger Inspect, 30 minutes after the first flagged reading at this cadence. Pressure below 1.5 bar or flow above 20 L/min triggers an immediate Urgent rule alert. Contiguous alert readings become one ticket. These illustrative limits require site approval. A technician checks sensor health, legitimate demand and pipe condition before any intervention. No valve, SMS or email action is automated.

AI Workflow and Practical Delivery

Abhishek Maurya  |  SustainAI Assignment 3B  |  Page 2

Maintenance and feedback loop

Tickets progress New → Acknowledged → Inspected → Resolved. Inspection requires an outcome and notes: confirmed leak, legitimate usage, sensor fault or inconclusive. Inconclusive cases stay open. A local SQLite event log preserves each update. Feedback supports expert review, drift checks and a later versioned baseline update; it never silently retrains the demo model.

Tools and feasible implementation

Python 3.12, pandas and NumPy validate data and calculate features; scikit-learn supplies a 200-tree Isolation Forest with seed 42; Streamlit and Altair provide CSV upload, historical charts, evidence and exports. SQLite supports a local inspection desk. README, pinned dependencies, dataset generator, automated tests and deployment instructions accompany the source.

Verification and honest impact measurement

The reproducible fixture contains 2,880 synthetic readings over 30 days. The first 1,920 contain no injected faults; the last 960 include a simulated leak, burst and pressure fault. Actual test results and synthetic confusion counts are recorded in VERIFIED_RESULTS.md and demo_metrics.json. These results do not establish field accuracy. No measured water or financial savings are claimed.

Privacy and path to a real pilot

Use de-identified readings; consumption patterns can expose occupancy. This local demo has no authentication or tenant isolation. A pilot needs access control, TLS, durable storage, retention policies, calibrated sensors, freshness monitoring and independently adjudicated events. An optional ESP32 → authenticated gateway → quality checks → historical CSV path is documented, but hardware integration is not implemented or tested.

Measure event recall, false tickets per zone-day and time to inspection on a real pilot before claiming benefit. Estimate avoided loss only with calibrated measurements and a defensible counterfactual. Fifteen-minute readings can miss short events; seasonal demand and sensor drift require review.

Technical references: scikit-learn 1.7 IsolationForest API; Streamlit Community Cloud dependency and file organization documentation. Full links and the five-criterion submission map are in README. This document covers AI use case, input-output mapping, workflow strength, feasibility and clarity.