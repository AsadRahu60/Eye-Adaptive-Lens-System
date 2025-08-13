from host.pi.context_engine import classify
import pytest


@pytest.mark.parametrize(
    "distance,lux,motion,expected",
    [
        (40, 100, 0, "near"),  # very close
        (None, 6000, 0, "outdoor"),  # bright ambient
        (80, 300, 0, "desk"),  # default
    ],
)
def test_classify(distance, lux, motion, expected):
    assert classify(distance, lux, motion) == expected
