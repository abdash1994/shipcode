import os
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

app = FastAPI()
if not os.environ.get("NOCORS"):
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class OrderIn(BaseModel):
    item: str
    qty: int = Field(gt=0)
    @field_validator("item")
    @classmethod
    def not_blank(cls, v):
        if not v.strip():
            raise ValueError("item must not be blank")
        return v.strip()

ORDERS, KEYS, NEXT = {}, {}, [1]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/orders", status_code=int(os.environ.get("CREATE_STATUS", "201")))
def create(o: OrderIn, idempotency_key: Optional[str] = Header(default=None)):
    if idempotency_key and idempotency_key in KEYS and not os.environ.get("NOIDEM"):
        return KEYS[idempotency_key]
    order = {"id": NEXT[0], "item": o.item, "qty": o.qty}
    ORDERS[order["id"]] = order
    NEXT[0] += 1
    if idempotency_key:
        KEYS[idempotency_key] = order
    return order

@app.get("/orders/{oid}")
def get_one(oid: int):
    if oid not in ORDERS:
        raise HTTPException(404, "not found")
    return ORDERS[oid]

@app.get("/orders")
def list_all():
    return {"orders": [ORDERS[i] for i in sorted(ORDERS)]}
