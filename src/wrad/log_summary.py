"""Summarize generic realtime audio metrics from JSONL or text logs."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


NUMERIC_KEYS = {
    "avg_ms",
    "max_ms",
    "late_chunks",
    "output_underflows",
    "input_overflows",
    "callback_jitter_ms",
    "target_prefill_ms",
    "ring_fill_ms",
    "peak_dbfs",
    "rms_dbfs",
    "clipped_sample_ratio",
}

BOOLEAN_KEYS = {
    "cache_enabled",
    "cache_warm",
    "gpu_cache_enabled",
    "model_cache_enabled",
}

PAIR_RE = re.compile(r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*(?:=|:)\s*(?P<value>[^,\s]+)")


@dataclass(frozen=True)
class MetricStats:
    count: int
    average: float
    minimum: float
    maximum: float
    latest: float


@dataclass(frozen=True)
class LogSummary:
    lines_seen: int
    records_parsed: int
    metrics: dict[str, MetricStats] = field(default_factory=dict)
    flags: dict[str, bool] = field(default_factory=dict)


def _parse_scalar(value: Any) -> Any:
    if isinstance(value, (bool, int, float)) or value is None:
        return value
    if not isinstance(value, str):
        return value
    cleaned = value.strip().strip('"').strip("'")
    lowered = cleaned.lower()
    if lowered in {"true", "yes", "on", "enabled"}:
        return True
    if lowered in {"false", "no", "off", "disabled"}:
        return False
    try:
        if any(part in lowered for part in (".", "e")):
            return float(cleaned)
        return int(cleaned)
    except ValueError:
        return cleaned


def parse_log_line(line: str) -> dict[str, Any]:
    """Parse one JSONL or simple key/value text log line."""

    stripped = line.strip()
    if not stripped:
        return {}
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict):
        return {str(key): _parse_scalar(value) for key, value in parsed.items()}

    values: dict[str, Any] = {}
    for match in PAIR_RE.finditer(stripped):
        values[match.group("key")] = _parse_scalar(match.group("value"))
    return values


def summarize_records(records: Iterable[dict[str, Any]], lines_seen: int | None = None) -> LogSummary:
    numeric_values: dict[str, list[float]] = {}
    flags: dict[str, bool] = {}
    parsed_count = 0

    for record in records:
        if not record:
            continue
        parsed_count += 1
        for key, value in record.items():
            normalized = key.strip()
            parsed_value = _parse_scalar(value)
            if normalized in BOOLEAN_KEYS and isinstance(parsed_value, bool):
                flags[normalized] = parsed_value
            if normalized in NUMERIC_KEYS and isinstance(parsed_value, (int, float)) and not isinstance(parsed_value, bool):
                numeric_values.setdefault(normalized, []).append(float(parsed_value))

    metrics = {
        key: MetricStats(
            count=len(values),
            average=sum(values) / len(values),
            minimum=min(values),
            maximum=max(values),
            latest=values[-1],
        )
        for key, values in sorted(numeric_values.items())
        if values
    }
    return LogSummary(lines_seen=parsed_count if lines_seen is None else lines_seen, records_parsed=parsed_count, metrics=metrics, flags=dict(sorted(flags.items())))


def summarize_lines(lines: Iterable[str]) -> LogSummary:
    parsed_records = []
    line_count = 0
    for line in lines:
        line_count += 1
        parsed_records.append(parse_log_line(line))
    return summarize_records(parsed_records, lines_seen=line_count)


def summarize_log_file(path: str | Path) -> LogSummary:
    with Path(path).open("r", encoding="utf-8") as handle:
        return summarize_lines(handle)


def summary_to_dict(summary: LogSummary) -> dict[str, Any]:
    data = asdict(summary)
    return data


def _print_text(summary: LogSummary) -> None:
    print(f"lines_seen: {summary.lines_seen}")
    print(f"records_parsed: {summary.records_parsed}")
    if summary.flags:
        print("flags:")
        for key, value in summary.flags.items():
            print(f"  {key}: {str(value).lower()}")
    if summary.metrics:
        print("metrics:")
        for key, stats in summary.metrics.items():
            print(
                f"  {key}: count={stats.count} avg={stats.average:.3f} "
                f"min={stats.minimum:.3f} max={stats.maximum:.3f} latest={stats.latest:.3f}"
            )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize generic realtime audio logs.")
    parser.add_argument("log_path", help="Path to a JSONL or text log file.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    summary = summarize_log_file(args.log_path)
    if args.json:
        print(json.dumps(summary_to_dict(summary), indent=2, sort_keys=True))
    else:
        _print_text(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
