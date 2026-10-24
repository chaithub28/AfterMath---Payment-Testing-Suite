# Aftermath | Payment Workflow Testing Suite

A beginner-friendly QA portfolio project that tests a **simulated payment API**. It does not connect to a real payment provider and does not move real money.

## Features
- FastAPI REST endpoints with JSON responses and HTTP status codes
- SQLite transaction persistence and SQL verification
- Positive and negative API scenarios
- Idempotency-key check to avoid duplicate transaction creation
- Automated pytest suite
- Postman collection and QA test documentation

## Requirements
- Python 3.10 or newer (the code uses modern Python typing)
- VS Code recommended

## Windows setup
Open this project folder in VS Code, then choose **Terminal → New Terminal**.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks environment activation, open Command Prompt as the VS Code terminal and use:
```bat
.venv\Scripts\activate.bat
```

## Run the API
From the project root (the folder containing `requirements.txt`):
```powershell
python -m uvicorn app.main:app --reload
```
Open:
- Health check: http://127.0.0.1:8000/
- Interactive API docs: http://127.0.0.1:8000/docs

Keep the terminal running while you use the API. Press `Ctrl+C` to stop it.

## Run automated tests
Open a second terminal in the project root, activate `.venv`, then run:
```powershell
python -m pytest -v
```

## Example requests
Successful payment:
```json
{"amount": 125.50, "currency": "INR", "description": "Test order"}
```

Simulated decline (a test-only switch, not a real card decline):
```json
{"amount": 80, "currency": "INR", "simulate_decline": true}
```

Duplicate prevention: send the same request twice with the same `Idempotency-Key` header, e.g. `order-abc-123`.

## Database verification
The database file `aftermath.db` is created in the project root when the API starts. If you have SQLite installed, use:
```sql
SELECT id, amount, currency, status, failure_reason, created_at
FROM payments
ORDER BY created_at DESC;

SELECT status, COUNT(*) AS transaction_count
FROM payments
GROUP BY status;
```

## Postman
Import `postman/Aftermath_Payment_API.postman_collection.json` into Postman. Start the API first.

## Project honesty note
Run the tests and verify their results before claiming they passed. Sample defect reports are templates/examples for learning; they are not claims of bugs discovered in a production system.
