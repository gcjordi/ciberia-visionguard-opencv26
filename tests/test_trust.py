from app.trust import TrustInputs, calculate_vcts, decide_action


def test_vcts_bounds_and_policy():
    v = calculate_vcts(TrustInputs(1, 1, 1, 1, 1))
    assert v.score == 100.0
    assert decide_action(v.score, True) == "ACT"
    assert decide_action(90, False) == "IGNORE"
    assert decide_action(70, True) == "VERIFY"
    assert decide_action(50, True) == "RE_OBSERVE"
    assert decide_action(20, True) == "HUMAN_REVIEW"


def test_vcts_weighted_value():
    v = calculate_vcts(TrustInputs(1, 0, 0, 0, 0))
    assert v.score == 25.0
