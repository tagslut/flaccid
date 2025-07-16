#!/usr/bin/env python3
"""
Unit tests for audio utility functions.
"""


from flaccid.utils.audio import (
    format_duration,
    format_size,
    get_audio_quality_score,
)


def test_format_size():
    """
    Test the format_size function correctly formats byte sizes.
    """
    assert format_size(0) == "0.00 B"
    assert format_size(1024) == "1.00 KB"
    assert format_size(1024 * 1024) == "1.00 MB"
    assert format_size(1024 * 1024 * 1024) == "1.00 GB"


def test_format_duration():
    """
    Test the format_duration function correctly formats seconds.
    """
    assert format_duration(0) == "0:00"
    assert format_duration(59) == "0:59"
    assert format_duration(60) == "1:00"
    assert format_duration(61) == "1:01"


def test_get_audio_quality_score():
    """
    Test the get_audio_quality_score function correctly scores audio quality.
    """
    # Test with empty metadata
    assert get_audio_quality_score({}) is None

    # Test with complete metadata
    metadata = {"sample_rate": 44100, "bits_per_sample": 16, "channels": 2}
    score = get_audio_quality_score(metadata)
    assert score is not None
    assert score > 0

    # Test with high quality metadata
    high_quality = {"sample_rate": 96000, "bits_per_sample": 24, "channels": 2}
    high_score = get_audio_quality_score(high_quality)
    assert high_score is not None
    assert high_score > score  # Higher quality should have higher score
