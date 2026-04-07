from host.pi.therapy import policy, VALID_MODES


def test_policy_near_sets_right_occlusion():
    l, r, shutters = policy("near", 0.0, 0.0)
    assert shutters["R"] == 50.0
    assert shutters["L"] == 0.0
    assert shutters["period_ms"] == 30_000


def test_policy_desk_mild_right_occlusion():
    """Desk mode applies a gentle 20 % right occlusion — not zero."""
    l, r, shutters = policy("desk", 0.0, 0.0)
    assert shutters["L"] == 0.0
    assert shutters["R"] == 20.0


def test_policy_outdoor_no_occlusion():
    """Outdoor mode should have zero occlusion on both eyes."""
    l, r, shutters = policy("outdoor", 0.0, 0.0)
    assert shutters["L"] == 0.0
    assert shutters["R"] == 0.0


def test_policy_base_diopters_passthrough():
    """Base diopter values must be returned unchanged."""
    l, r, _ = policy("near", 1.5, -0.75)
    assert l == 1.5
    assert r == -0.75


def test_policy_unknown_mode_falls_back_to_desk():
    """Unknown modes must not crash — they fall back to 'desk'."""
    l, r, shutters = policy("unknown_mode", 0.0, 0.0)
    assert shutters["R"] == 20.0  # desk default


def test_all_valid_modes_exist():
    assert VALID_MODES == {"near", "desk", "outdoor"}
