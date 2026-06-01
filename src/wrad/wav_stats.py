"""Analyze WAV files for clipping and level statistics."""

from __future__ import annotations

import argparse
import json
import math
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class WavStats:
    path: str
    duration_seconds: float
    sample_rate: int
    channels: int
    frames: int
    sample_width_bytes: int
    peak_amplitude: float
    rms_amplitude: float
    peak_dbfs: float
    rms_dbfs: float
    clipped_sample_ratio: float


def _dbfs(amplitude: float) -> float:
    if amplitude <= 0:
        return float("-inf")
    return 20.0 * math.log10(amplitude)


def _pcm_to_float(raw: bytes, sample_width: int) -> np.ndarray:
    if sample_width == 1:
        data = np.frombuffer(raw, dtype=np.uint8).astype(np.float64)
        return (data - 128.0) / 128.0
    if sample_width == 2:
        data = np.frombuffer(raw, dtype="<i2").astype(np.float64)
        return data / 32768.0
    if sample_width == 3:
        bytes_ = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        sign = (bytes_[:, 2] & 0x80) != 0
        padded = np.zeros((bytes_.shape[0], 4), dtype=np.uint8)
        padded[:, :3] = bytes_
        padded[sign, 3] = 0xFF
        data = padded.view("<i4").reshape(-1).astype(np.float64)
        return data / 8388608.0
    if sample_width == 4:
        data = np.frombuffer(raw, dtype="<i4").astype(np.float64)
        return data / 2147483648.0
    raise ValueError(f"Unsupported PCM sample width: {sample_width} bytes")


def analyze_wav(path: str | Path) -> WavStats:
    """Return level and clipping statistics for an uncompressed PCM WAV file."""

    wav_path = Path(path)
    with wave.open(str(wav_path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_rate = wav_file.getframerate()
        frames = wav_file.getnframes()
        sample_width = wav_file.getsampwidth()
        compression = wav_file.getcomptype()
        raw = wav_file.readframes(frames)

    if compression != "NONE":
        raise ValueError(f"Unsupported WAV compression type: {compression}")

    samples = _pcm_to_float(raw, sample_width)
    finite_samples = samples[np.isfinite(samples)]
    if finite_samples.size == 0:
        peak = 0.0
        rms = 0.0
        clipped_ratio = 0.0
    else:
        abs_samples = np.abs(finite_samples)
        peak = float(np.max(abs_samples))
        rms = float(np.sqrt(np.mean(np.square(finite_samples))))
        clipped_ratio = float(np.count_nonzero(abs_samples >= 1.0) / finite_samples.size)

    return WavStats(
        path=str(wav_path),
        duration_seconds=frames / sample_rate if sample_rate else 0.0,
        sample_rate=sample_rate,
        channels=channels,
        frames=frames,
        sample_width_bytes=sample_width,
        peak_amplitude=peak,
        rms_amplitude=rms,
        peak_dbfs=_dbfs(peak),
        rms_dbfs=_dbfs(rms),
        clipped_sample_ratio=clipped_ratio,
    )


def stats_to_dict(stats: WavStats) -> dict[str, Any]:
    return asdict(stats)


def _print_text(stats: WavStats) -> None:
    print(f"path: {stats.path}")
    print(f"duration_seconds: {stats.duration_seconds:.6f}")
    print(f"sample_rate: {stats.sample_rate}")
    print(f"channels: {stats.channels}")
    print(f"frames: {stats.frames}")
    print(f"sample_width_bytes: {stats.sample_width_bytes}")
    print(f"peak_amplitude: {stats.peak_amplitude:.9f}")
    print(f"rms_amplitude: {stats.rms_amplitude:.9f}")
    print(f"peak_dbfs: {stats.peak_dbfs:.3f}")
    print(f"rms_dbfs: {stats.rms_dbfs:.3f}")
    print(f"clipped_sample_ratio: {stats.clipped_sample_ratio:.9f}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze WAV clipping and level statistics.")
    parser.add_argument("wav_path", help="Path to a WAV file.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    stats = analyze_wav(args.wav_path)
    if args.json:
        print(json.dumps(stats_to_dict(stats), indent=2, sort_keys=True))
    else:
        _print_text(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
