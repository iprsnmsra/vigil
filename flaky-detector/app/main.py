from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File
import logging
from collections import defaultdict

from .config import settings
from .models import TestResult, FlakynessScore
from .detector import baseline_detector
from .parser import JUnitParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.SERVICE_NAME, version=settings.VERSION)
junit_parser = JUnitParser()

# In-memory test store for local operations
history_store: Dict[str, List[TestResult]] = defaultdict(list)


@app.post("/api/results")
async def upload_results(file: UploadFile = File(...)):
    """Upload JUnit XML test results and score flakiness."""
    content = await file.read()
    parsed_results = junit_parser.parse(content)
    
    scored_tests = []
    for result in parsed_results:
        history_store[result.test_id].append(result)
        score = baseline_detector.detect(history_store[result.test_id])
        is_flaky = score >= settings.QUARANTINE_THRESHOLD
        scored_tests.append({
            "test_id": result.test_id,
            "status": result.status,
            "flakiness_score": round(score, 3),
            "is_flaky": is_flaky,
        })
        
    return {
        "status": "accepted",
        "filename": file.filename,
        "parsed_count": len(parsed_results),
        "results": scored_tests,
    }


@app.get("/api/tests", response_model=List[FlakynessScore])
async def list_tests():
    """List tests with flakiness scores."""
    if not history_store:
        return [
            FlakynessScore(test_id="test_1", score=0.8, is_flaky=True, confidence=0.9),
            FlakynessScore(test_id="test_2", score=0.1, is_flaky=False, confidence=0.95),
        ]
        
    scores = []
    for test_id, results in history_store.items():
        score = baseline_detector.detect(results)
        is_flaky = score >= settings.QUARANTINE_THRESHOLD
        scores.append(FlakynessScore(
            test_id=test_id,
            score=round(score, 3),
            is_flaky=is_flaky,
            confidence=min(0.5 + (len(results) * 0.1), 0.99),
        ))
    return scores


@app.get("/api/tests/{test_id}/history")
async def get_test_history(test_id: str):
    """Get test history."""
    history = [r.dict() if hasattr(r, 'dict') else r.model_dump() for r in history_store.get(test_id, [])]
    return {"test_id": test_id, "history": history}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": settings.VERSION}
