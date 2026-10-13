from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class TestResult(BaseModel):
    test_id: str
    name: str
    classname: str
    status: str
    duration: float
    timestamp: datetime = datetime.utcnow()

class TestHistory(BaseModel):
    test_id: str
    results: List[TestResult]

class FlakynessScore(BaseModel):
    test_id: str
    score: float
    is_flaky: bool
    confidence: float

class QuarantineRequest(BaseModel):
    test_id: str
    reason: str

# SQLAlchemy models (stubs)
class TestResultDB:
    pass

class TestHistoryDB:
    pass
