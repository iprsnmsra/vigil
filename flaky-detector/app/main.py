from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File
import logging

from .config import settings
from .models import TestResult, FlakynessScore
from .detector import baseline_detector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.SERVICE_NAME, version=settings.VERSION)

@app.post("/api/results")
async def upload_results(file: UploadFile = File(...)):
    """Upload JUnit XML test results."""
    # In a real app we'd parse the file here
    return {"status": "accepted", "filename": file.filename}

@app.get("/api/tests", response_model=List[FlakynessScore])
async def list_tests():
    """List tests with flakiness scores."""
    # Dummy data
    return [
        FlakynessScore(test_id="test_1", score=0.8, is_flaky=True, confidence=0.9),
        FlakynessScore(test_id="test_2", score=0.1, is_flaky=False, confidence=0.95)
    ]

@app.get("/api/tests/{test_id}/history")
async def get_test_history(test_id: str):
    """Get test history."""
    return {"test_id": test_id, "history": []}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": settings.VERSION}
