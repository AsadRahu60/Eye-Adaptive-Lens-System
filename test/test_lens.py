from host.pi.lens_controller import ramp_focus


def test_ramp_focus_runs_and_reaches_target():
    path = ramp_focus(0.0, 1.0, duration_s=2.0, steps=10, sleep=False)
    assert len(path) == 11
    assert abs(path[-1] - 1.0) < 1e-9
