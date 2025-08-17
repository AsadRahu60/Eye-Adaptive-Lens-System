from host.pi.lens_controller import ramp_focus


def test_ramp_focus_runs():
    ramp_focus(0, 1, 2)  # should not raise
    assert True  # If no exception is raised, the test passes
