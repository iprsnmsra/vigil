import random
import time
from typing import List
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel
from app.config import settings

app = FastAPI(title=settings.SERVICE_NAME, version=settings.VERSION)

# Prometheus metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Handle failure modes
    if request.url.path.startswith("/api/orders"):
        if settings.FAILURE_MODE == "error" and random.random() < 0.5:
            http_requests_total.labels(method=request.method, endpoint=request.url.path, status="500").inc()
            return Response(content="Internal Server Error due to FAILURE_MODE", status_code=500)
        elif settings.FAILURE_MODE == "slow":
            time.sleep(2)

    try:
        response = await call_next(request)
        status_code = str(response.status_code)
    except Exception as e:
        status_code = "500"
        raise e
    finally:
        duration = time.time() - start_time
        endpoint = request.url.path
        http_requests_total.labels(method=request.method, endpoint=endpoint, status=status_code).inc()
        http_request_duration_seconds.labels(method=request.method, endpoint=endpoint).observe(duration)
        
    return response

class OrderCreate(BaseModel):
    product_id: int
    quantity: int

class Order(BaseModel):
    id: int
    product_id: int
    quantity: int
    status: str
    created_at: str

orders_db = [
    Order(id=1, product_id=1, quantity=1, status="shipped", created_at=datetime.now(timezone.utc).isoformat()),
    Order(id=2, product_id=2, quantity=2, status="pending", created_at=datetime.now(timezone.utc).isoformat()),
    Order(id=3, product_id=3, quantity=1, status="delivered", created_at=datetime.now(timezone.utc).isoformat()),
    Order(id=4, product_id=4, quantity=1, status="processing", created_at=datetime.now(timezone.utc).isoformat()),
    Order(id=5, product_id=5, quantity=3, status="pending", created_at=datetime.now(timezone.utc).isoformat()),
]
next_id = 6

@app.get("/health")
def health():
    return {"status": "healthy", "service": settings.SERVICE_NAME, "version": settings.VERSION}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/orders", response_model=List[Order])
def list_orders():
    return orders_db

@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    for o in orders_db:
        if o.id == order_id:
            return o
    raise HTTPException(status_code=404, detail="Order not found")

@app.post("/api/orders", response_model=Order, status_code=201)
def create_order(order: OrderCreate):
    global next_id
    new_order = Order(
        id=next_id,
        product_id=order.product_id,
        quantity=order.quantity,
        status="pending",
        created_at=datetime.now(timezone.utc).isoformat()
    )
    orders_db.append(new_order)
    next_id += 1
    return new_order
