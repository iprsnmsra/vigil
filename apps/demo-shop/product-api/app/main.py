import random
import time
from typing import List
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
    if request.url.path.startswith("/api/products"):
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

class Product(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool

products_db = [
    Product(id=1, name="Laptop", price=999.99, in_stock=True),
    Product(id=2, name="Mouse", price=29.99, in_stock=True),
    Product(id=3, name="Keyboard", price=59.99, in_stock=False),
    Product(id=4, name="Monitor", price=199.99, in_stock=True),
    Product(id=5, name="Headphones", price=89.99, in_stock=True),
]

@app.get("/health")
def health():
    return {"status": "healthy", "service": settings.SERVICE_NAME, "version": settings.VERSION}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/products", response_model=List[Product])
def list_products():
    return products_db

@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    for p in products_db:
        if p.id == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")
