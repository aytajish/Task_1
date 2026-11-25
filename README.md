# QueueFlow

A lightweight appointment booking platform for small service businesses.

## Features
- Public booking form
- Business dashboard
- Confirm, complete, and cancel appointments
- SQLite persistence
- English and Azerbaijani UI

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:10000

## Deploy to Render
Create a new **Web Service** from this repository. Render detects `render.yaml` and applies the included configuration. Set a persistent disk mounted at `/var/data` if deploying without Blueprint support.
