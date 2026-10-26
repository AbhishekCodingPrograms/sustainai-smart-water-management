# Deployment and operation

## Local reproducible demonstration

Use Python 3.12 and the README setup. Keep the terminal open while using the app. Stop it with Ctrl+C. Regenerate the fixture with the documented seed and run tests before changes. The runtime database is created only when the inspection page executes; tests use temporary databases.

## Optional Streamlit Community Cloud demo

1. Put the extracted project in a repository you control. Exclude `.venv`, runtime databases, uploads, credentials and caches.
2. Create a Streamlit Community Cloud app, choose that repository and `app.py` as its entry point. Python 3.12 is the original tested runtime; the current requirements also provide Python 3.14 wheels for cloud deployments that select 3.14.
3. Keep `requirements.txt` next to `app.py`. Use only the bundled synthetic data in a public demonstration.
4. Check build logs, then verify initial render, chart interaction, validation errors and export. Create a test ticket and confirm the inspection flow.
5. SQLite on hosted temporary storage is not durable. Use an authenticated service and managed database before relying on inspection history. No public cloud deployment was performed for this submission.

See the official Streamlit dependency and file-organization references in README for the current hosting requirements.

### Python 3.14 dependency build fix

If logs show `Building numpy==2.2.6` or `Building pandas==2.2.3` under Python 3.14, the original package pins are being installed. Those versions predate Python 3.14 wheels. Current `requirements.txt` uses NumPy 2.3.3 and pandas 2.3.3, both with Python 3.14 binary wheels. Streamlit 1.52.2 and Altair 6.0.0 also replace the old UI pins: Altair 5.5.0 raises a `TypedDict` import error on Python 3.14. The scikit-learn model version is unchanged. Pull the latest `main` commit and let Community Cloud rebuild dependencies. If a failed build does not restart automatically, select **Reboot app** from the app management menu. Check for the updated package versions in the new logs.

Use `requirements.txt` for the cloud app; the original Python 3.12 package snapshot is retained separately in `docs/requirements-original-py312.txt`. Do not use that historical snapshot to install on Python 3.14. A repository `runtime.txt` or `.python-version` file is not a substitute for Community Cloud's Python selector. Changing an existing app's Python version requires deletion and redeployment according to [Streamlit's Python upgrade guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/upgrade-python); the dependency update avoids that step for this issue.

## Private pilot readiness

This demonstration is not hardened for public or operational use. Add identity and access control, separate organizations/zones, role-based inspection permissions, TLS, encrypted backups, durable managed storage and retention controls. Validate sensor timestamps and aggregation upstream; implement freshness checks, device heartbeat and missing-data alerts rather than interpreting silence as normal. Monitor ingestion failure, model drift and ticket volume.

Approve engineering thresholds with site staff; collect representative normal history; validate on independent labelled events. Establish rollback, incident response, backup recovery, observability and software patching. Review dependency vulnerabilities before deployment. Do not upload serialized model files from untrusted sources. Document a hardware safety case separately if proposing future valve control.
