import cv2
import numpy as np

from app.vision import detect_motion, image_quality, stress_test_pair


def make_pair():
    h, w = 240, 400
    prev = np.full((h, w, 3), 80, dtype=np.uint8)
    cur = prev.copy()
    cv2.rectangle(cur, (300, 80), (365, 190), (230, 230, 230), -1)
    return prev, cur


def test_motion_in_restricted_zone():
    prev, cur = make_pair()
    ev = detect_motion(prev, cur, zone_start=.68)
    assert ev.present
    assert ev.in_restricted_zone
    assert ev.confidence > 0


def test_quality_is_bounded():
    _, cur = make_pair()
    q = image_quality(cur)
    assert 0 <= q.overall <= 1


def test_stress_has_five_cases():
    prev, cur = make_pair()
    ev = detect_motion(prev, cur, zone_start=.68)
    results = stress_test_pair(prev, cur, ev)
    assert len(results) == 5
