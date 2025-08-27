
# Project CRUD (Flask)

A ready-to-run CRUD web app for a **Project** entity with a **progress** attribute (between start and end date)
and an additional **progress entries** log you can append to over time.

## Local quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app run
# Open http://localhost:5000
```

The SQLite database (`db.sqlite3`) will be created automatically on first run.

## Deploy on Render

1. Push this folder to a public Git repository (GitHub/GitLab/Bitbucket).
2. In Render, create a **New Web Service** from that repo.
3. Render will detect `render.yaml` or use:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. (Optional but recommended) Add a managed **PostgreSQL** database on Render and set the `DATABASE_URL` env var. The app automatically switches from SQLite to Postgres if `DATABASE_URL` is present.

## Data model

- `Project`: id, name, description, start_date, **progress**, end_date, status
- `ProgressEntry`: id, project_id → Project, content, created_at

In the form UI, **progress** is intentionally placed between **start date** and **end date**.

## Notes

- CSRF protection is enabled via `SECRET_KEY`.
- Search by name/description/progress/status on the Projects list page.
- To reset locally, delete `db.sqlite3` and re-run the app.
