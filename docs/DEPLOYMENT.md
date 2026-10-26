# Deployment and operation

## Local reproducible demonstration

Use Python 3.12 and the README setup. Keep the terminal open while using the app. Stop it with Ctrl+C. Regenerate the fixture with the documented seed and run tests before changes. The runtime database is created only when the inspection page executes; tests use temporary databases.

## Optional Streamlit Community Cloud demo

1. Put the extracted project in a repository you control. Exclude `.venv`, runtime databases, uploads, credentials and caches.
2. Create a Streamlit Community Cloud app, choose that repository and `app.py` as its entry point. Select Python 3.12 under the deployment settings.
3. Keep `requirements.txt` next to `app.py`. Use only the bundled synthetic data in a public demonstration.
4. Check build logs, then verify initial render, chart interaction, validation errors and export. Create a test ticket and confirm the inspection flow.
5. SQLite on hosted temporary storage is not durable. Use an authenticated service and managed database before relying on inspection history. No public cloud deployment was performed for this submission.

See the official Streamlit dependency and file-organization references in README for the current hosting requirements.

## Private pilot readiness

This demonstration is not hardened for public or operational use. Add identity and access control, separate organizations/zones, role-based inspection permissions, TLS, encrypted backups, durable managed storage and retention controls. Validate sensor timestamps and aggregation upstream; implement freshness checks, device heartbeat and missing-data alerts rather than interpreting silence as normal. Monitor ingestion failure, model drift and ticket volume.

Approve engineering thresholds with site staff; collect representative normal history; validate on independent labelled events. Establish rollback, incident response, backup recovery, observability and software patching. Review dependency vulnerabilities before deployment. Do not upload serialized model files from untrusted sources. Document a hardware safety case separately if proposing future valve control.
