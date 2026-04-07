import logging
from host.pi.lens_controller import ramp, OptoLens


def test_ramp_caps_rate():
    # max change = rate * dt = 0.25 * 0.1 = 0.025
    assert ramp(0.0, 1.0, 0.25, 0.1) == 0.025


def test_set_diopter_runs_in_dry_run(caplog):
    """Dry-run mode must return 'OK' and emit a DEBUG log containing the command."""
    with caplog.at_level(logging.DEBUG, logger="host.pi.lens_controller"):
        lens = OptoLens(None)  # dry-run mode: no serial port required
        resp = lens.set_diopter(1.23)

    assert resp == "OK"
    # The DRY-RUN log message must include the command sent
    dry_run_messages = [r.message for r in caplog.records if "DRY-RUN" in r.message]
    assert dry_run_messages, "Expected a DRY-RUN debug log entry"
    assert "1.23" in dry_run_messages[0]
