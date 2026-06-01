# windows-realtime-audio-diagnostics

[![Python tests](https://github.com/yamyamrvc-jpg/windows-realtime-audio-diagnostics/actions/workflows/python-tests.yml/badge.svg)](https://github.com/yamyamrvc-jpg/windows-realtime-audio-diagnostics/actions/workflows/python-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Small, practical diagnostics for developers building low-latency realtime audio applications on Windows.

This toolkit was created from practical realtime audio debugging needs: checking WAV clipping, summarizing callback timing logs, spotting output underflows, and documenting virtual audio routing. It is generic by design and focuses on observable files, logs, and device notes.

## Features

- Analyze WAV files for duration, sample rate, channel count, peak, RMS, dBFS, and clipped sample ratio.
- Summarize realtime audio logs from JSONL or simple text logs.
- Extract common metrics when present: `avg_ms`, `max_ms`, `late_chunks`, `output_underflows`, `input_overflows`, `callback_jitter_ms`, `target_prefill_ms`, `ring_fill_ms`, and cache enabled flags.
- Provide Windows device routing notes and checklists for virtual microphone workflows.
- Keep outputs plain and script-friendly.

## Installation

```powershell
python -m pip install .
```

For development:

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## Command Examples

Analyze a WAV file:

```powershell
python -m wrad.wav_stats path\to\audio.wav
```

Print JSON output:

```powershell
python -m wrad.wav_stats path\to\audio.wav --json
```

Summarize a realtime audio log:

```powershell
python -m wrad.log_summary examples\sample_realtime_log.jsonl
```

Summarize simple text logs:

```powershell
python -m wrad.log_summary path\to\audio.log --json
```

Print CSV summary output:

```powershell
python -m wrad.log_summary examples\sample_realtime_log.jsonl --format csv
```

Print a Windows routing checklist:

```powershell
python -m wrad.device_notes
```

## Python Examples

```python
from wrad.wav_stats import analyze_wav

stats = analyze_wav("capture.wav")
print(stats.peak_dbfs, stats.clipped_sample_ratio)
```

```python
from wrad.log_summary import summarize_log_file

summary = summarize_log_file("realtime.jsonl")
print(summary.metrics)
```

## Log Input Format

`wrad.log_summary` accepts JSON Lines:

```json
{"avg_ms": 4.2, "max_ms": 8.9, "late_chunks": 0, "output_underflows": 0}
```

It also accepts simple text lines containing `key=value` or `key: value` pairs:

```text
callback avg_ms=4.2 max_ms=8.9 late_chunks=1 output_underflows=0 cache_enabled=true
```

Missing fields are tolerated. Numeric metrics are summarized with count, average, min, max, and latest value.

## Roadmap

- Keep log parsing tolerant while adding small, well-tested output formats.
- Improve examples for common Windows audio troubleshooting workflows.
- Add documentation based on repeatable diagnostics rather than application-specific assumptions.

## Limitations

- WAV analysis focuses on uncompressed PCM WAV files supported by Python's standard `wave` module.
- Log parsing is intentionally tolerant and generic; it does not understand every application's custom schema.
- The toolkit diagnoses observable files and logs. It does not implement realtime processing engines or application-specific audio pipelines.
- Virtual audio cable guidance is a troubleshooting checklist, not a replacement for driver or OS-level diagnostics.

## Project Status

Initial public release. APIs are small and may evolve based on practical feedback.

## License

MIT. See [LICENSE](LICENSE).
