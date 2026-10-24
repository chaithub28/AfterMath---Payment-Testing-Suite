"""Aftermath Payment Workflow Testing Suite - simulated payment API."""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from app.database import (
    find_by_id, find_by_idempotency_key, init_db, insert_payment, list_payments
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Aftermath Payment Workflow Testing Suite",
    description="A local, simulated payment API for learning QA and API testing. No real money is moved.",
    version="1.0.0",
    lifespan=lifespan,
)

class PaymentRequest(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2, examples=["25.00"])
    currency: str = Field(default="INR", min_length=3, max_length=3)
    description: str | None = Field(default=None, max_length=200)
    simulate_decline: bool = False

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value):
        value = value.upper()
        if not value.isalpha():
            raise ValueError("Currency must contain three letters")
        return value

@app.get("/", tags=["Health"])
def home():
    return {"message": "Welcome to Aftermath Payment Testing Suite", "status": "running"}

@app.post("/payments", status_code=201, tags=["Payments"])
def create_payment(payload: PaymentRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    # Repeating a key returns the original transaction rather than creating a second payment.
    existing = find_by_idempotency_key(idempotency_key)
    if existing:
        return {"message": "Existing payment returned; duplicate was not created", "payment": existing}

    amount = float(payload.amount.quantize(Decimal("0.01")))
    failed = payload.simulate_decline
    payment = {
        "id": "pay_" + uuid4().hex[:12],
        "amount": amount,
        "currency": payload.currency,
        "status": "failed" if failed else "succeeded",
        "description": payload.description,
        "idempotency_key": idempotency_key,
        "failure_reason": "simulated_decline" if failed else None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    insert_payment(payment)
    return {"message": "Payment declined" if failed else "Payment processed", "payment": payment}

@app.get("/payments/{payment_id}", tags=["Payments"])
def get_payment(payment_id: str):
    payment = find_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"payment": payment}

@app.get("/payments", tags=["Payments"])
def get_payments(limit: int = Query(default=50, ge=1, le=100)):
    return {"payments": list_payments(limit)}
