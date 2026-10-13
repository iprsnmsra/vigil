import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_junit_xml():
    return b"""<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="tests" tests="2" failures="1" errors="0" skipped="0">
    <testcase classname="test_example" name="test_pass" time="0.1"/>
    <testcase classname="test_example" name="test_fail" time="0.2">
      <failure message="assertion failed"/>
    </testcase>
  </testsuite>
</testsuites>
"""
