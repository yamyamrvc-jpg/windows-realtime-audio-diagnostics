from __future__ import annotations

import math
import tempfile
import unittest
import wave

import numpy as np

from wrad.wav_stats import analyze_wav


def _write_wav(path, samples: np.ndarray, sample_rate: int = 8000) -> None:
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.astype("<i2").tobytes())


class WavStatsTests(unittest.TestCase):
    def test_analyze_wav_reports_basic_stats(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            wav_path = f"{tmp_dir}/tone.wav"
            samples = np.array([0, 16384, -16384, 0], dtype=np.int16)
            _write_wav(wav_path, samples)

            stats = analyze_wav(wav_path)

        self.assertEqual(stats.sample_rate, 8000)
        self.assertEqual(stats.channels, 1)
        self.assertEqual(stats.frames, 4)
        self.assertEqual(stats.duration_seconds, 4 / 8000)
        self.assertEqual(stats.peak_amplitude, 0.5)
        self.assertTrue(math.isclose(stats.rms_amplitude, math.sqrt(0.125), rel_tol=1e-9))
        self.assertTrue(math.isclose(stats.peak_dbfs, -6.020599913, rel_tol=1e-6))
        self.assertEqual(stats.clipped_sample_ratio, 0.0)

    def test_analyze_wav_detects_negative_full_scale_clip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            wav_path = f"{tmp_dir}/clip.wav"
            samples = np.array([0, -32768, 32767, 100], dtype=np.int16)
            _write_wav(wav_path, samples)

            stats = analyze_wav(wav_path)

        self.assertEqual(stats.peak_amplitude, 1.0)
        self.assertEqual(stats.peak_dbfs, 0.0)
        self.assertEqual(stats.clipped_sample_ratio, 0.25)


if __name__ == "__main__":
    unittest.main()
