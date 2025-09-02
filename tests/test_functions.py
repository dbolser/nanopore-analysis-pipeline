import os
import sys
import numpy as np
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Data_Load_Preprocessing import normalise_trace
from Event_classification import classify_events


def test_normalise_trace_constant_signal():
    data = np.column_stack((np.arange(5), np.ones(5) * 5))
    normalized, baseline = normalise_trace(
        data,
        baseline_method="moving_average",
        window_size=3,
    )
    assert np.allclose(baseline, np.ones(5) * 5)
    assert np.allclose(normalized[:, 1], np.zeros(5))


def test_normalise_trace_invalid_method():
    data = np.column_stack((np.arange(5), np.ones(5)))
    with pytest.raises(ValueError):
        normalise_trace(data, baseline_method="invalid")


def test_normalise_trace_downsample_sg_with_offset():
    data = np.column_stack((np.arange(8), np.zeros(8)))
    normalized, baseline = normalise_trace(
        data,
        baseline_method="sg",
        downsample_baseline=True,
        baseline_sample_time_us=30,
        manual_offset=1,
    )
    assert np.allclose(baseline, -1)
    assert np.allclose(normalized[:, 1], np.ones(8))


def test_normalise_trace_als_method():
    data = np.column_stack((np.arange(5), np.ones(5) * 2))
    normalized, baseline = normalise_trace(data, baseline_method="als")
    assert np.allclose(baseline, np.ones(5) * 2)
    assert np.allclose(normalized[:, 1], np.zeros(5), atol=1e-7)


def test_classify_events_basic():
    time = np.arange(100) / 1000  # 1000 Hz sample rate -> 1 ms per point
    signal = np.zeros(100)
    signal[10:12] = [1, 2]  # short, low SNR event -> ADEPT
    signal[20:40] = 5  # longer, high SNR event -> CUSUM
    data = np.column_stack((time, signal))
    event_boundaries = [(10, 12), (20, 40)]
    adept, cusum = classify_events(
        data,
        event_boundaries,
        noise_std=1,
        noise_mean=0,
        sample_rate=1000,
        short_event_duration_ms=2,
        snr_threshold=4,
    )
    assert len(adept) == 1 and adept[0]["event_idx"] == 0
    assert len(cusum) == 1 and cusum[0]["event_idx"] == 1


def test_classify_events_invalid_data():
    with pytest.raises(ValueError):
        classify_events(np.array([1, 2, 3]), [], 1, 0, 1000)


def test_classify_events_low_snr_overrides_duration():
    time = np.arange(100) / 1000
    signal = np.zeros(100)
    signal[10:50] = 1  # long duration but low amplitude
    data = np.column_stack((time, signal))
    adept, cusum = classify_events(
        data,
        [(10, 50)],
        noise_std=1,
        noise_mean=0,
        sample_rate=1000,
        short_event_duration_ms=2,
        snr_threshold=4,
    )
    assert len(adept) == 1 and len(cusum) == 0

