from lxml import etree
from typing import List
from .models import TestResult

class JUnitParser:
    def parse(self, content: bytes) -> List[TestResult]:
        """Parses JUnit XML content and returns TestResult objects."""
        results = []
        try:
            root = etree.fromstring(content)
            for testcase in root.xpath("//testcase"):
                name = testcase.get("name", "unknown")
                classname = testcase.get("classname", "unknown")
                time_str = testcase.get("time", "0.0")
                duration = float(time_str)
                
                status = "passed"
                if testcase.find("failure") is not None:
                    status = "failed"
                elif testcase.find("error") is not None:
                    status = "error"
                elif testcase.find("skipped") is not None:
                    status = "skipped"
                    
                test_id = f"{classname}.{name}"
                results.append(TestResult(
                    test_id=test_id,
                    name=name,
                    classname=classname,
                    status=status,
                    duration=duration
                ))
        except Exception as e:
            pass # Handle parsing errors
        return results
