from host.pi.therapy import policy


def test_policy_near_sets_right_occlusion():
    l, r, shutters = policy("near", 0.0, 0.0)
    assert shutters["R"] == 50.0
    assert shutters["L"] == 0.0
    assert shutters["period_ms"] == 30000


def test_policy_default_no_occlusion():
    l, r, shutters = policy("desk", 0.0, 0.0)
    assert shutters["L"] == 0.0 and shutters["R"] == 0.0
