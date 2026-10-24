# Test Cases — Aftermath Payment Workflow Testing Suite

Base URL: `http://127.0.0.1:8000`

| ID | Scenario | Request | Expected result |
|---|---|---|---|
| TC-001 | Health check | `GET /` | 200; status is `running` |
| TC-002 | Valid payment | `POST /payments`, amount 125.50 | 201; status `succeeded`; record stored |
| TC-003 | Simulated decline | `POST /payments`, `simulate_decline: true` | 201; status `failed` |
| TC-004 | Zero amount | `POST /payments`, amount 0 | 422 validation error |
| TC-005 | Negative amount | `POST /payments`, amount -1 | 422 validation error |
| TC-006 | Missing amount | `POST /payments`, omit amount | 422 validation error |
| TC-007 | Unknown transaction | `GET /payments/pay_unknown` | 404 |
| TC-008 | Duplicate idempotency key | Repeat POST with same `Idempotency-Key` | Same payment ID returned; no duplicate row |
| TC-009 | Invalid currency | Currency contains non-letters | 422 validation error |
| TC-010 | List transactions | `GET /payments` | 200; response contains payment list |

## Execution record
Fill this in only after running the tests.

| Run date | Passed | Failed | Notes |
|---|---:|---:|---|
| Not run yet | — | — | Pending local execution |
