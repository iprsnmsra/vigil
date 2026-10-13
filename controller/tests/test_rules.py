from app.rules import RuleEngine, Rule

def test_rule_matching():
    engine = RuleEngine()
    engine.rules = [
        Rule(
            name="TestRule",
            alert_match={"alertname": "TestAlert"},
            conditions=[],
            actions=[{"type": "restart"}],
            cooldown="1m"
        )
    ]
    
    alert = {"labels": {"alertname": "TestAlert", "severity": "high"}}
    match = engine.match_alert(alert)
    assert match is not None
    assert match.name == "TestRule"
    
    alert2 = {"labels": {"alertname": "OtherAlert"}}
    match2 = engine.match_alert(alert2)
    assert match2 is None
