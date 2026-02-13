# SolarOS Backend

Condition-based sustainability optimization for solar. This model demonstrates condition-based sustainability optimization at small scale. At utility scale, the impact multiplies significantly.

## Run locally

From the **project root** (SolarOS), not from `backend/`:

```bash
# Install deps (from project root)
pip install -r backend/requirements.txt

# Run API
uvicorn backend.main:app --reload --host 0.0.0.0
```

- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

## Endpoints

- `GET /` — service info and positioning statement
- `GET /analyze?cleaning_date_override=YYYY-MM-DD&days=30` — run 30-day scenario comparison (optional override for stress tests)

## Stress test

With the server running:

```bash
python backend/stress_test.py
```

Checks:

- Early cleaning (day 5) → negative net gain
- Late cleaning (day 25) → lower recoverable capture %
- Recommended date in logical window

## Deploy

Run from **project root** so `ml` resolves. Set the app module:

- **Render / Railway / similar**: Start command `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Docker**: Use `WORKDIR` at project root and `CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0"]`

Ensure `PORT` is read from the environment if the platform sets it.
