from host.pi.lens_controller import ramp, OptoLens


def test_ramp_caps_rate():
    # max change = rate * dt = 0.25 * 0.1 = 0.025
    assert ramp(0.0, 1.0, 0.25, 0.1) == 0.025


def test_set_diopter_runs_in_dry_run(capsys):
    lens = OptoLens(None)  # dry-run mode: no serial port required
    resp = lens.set_diopter(1.23)
    out = capsys.readouterr().out.strip()
    assert "DRY-RUN" in out and "1.23" in out
    assert resp == "OK"
