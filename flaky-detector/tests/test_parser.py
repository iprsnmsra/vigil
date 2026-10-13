from app.parser import JUnitParser

def test_junit_parser(sample_junit_xml):
    parser = JUnitParser()
    results = parser.parse(sample_junit_xml)
    
    assert len(results) == 2
    assert results[0].status == "passed"
    assert results[0].test_id == "test_example.test_pass"
    assert results[1].status == "failed"
    assert results[1].test_id == "test_example.test_fail"
