from __future__ import annotations

import csv
import io
from contextlib import redirect_stdout
import unittest

from wrad.log_summary import main, parse_log_line, summarize_lines, summary_to_csv


class LogSummaryTests(unittest.TestCase):
    def test_parse_json_line(self) -> None:
        record = parse_log_line('{"avg_ms": 4.2, "cache_enabled": true}')

        self.assertEqual(record, {"avg_ms": 4.2, "cache_enabled": True})

    def test_parse_text_line(self) -> None:
        record = parse_log_line("callback avg_ms=4.2 max_ms: 9 late_chunks=1 cache_enabled=true")

        self.assertEqual(record["avg_ms"], 4.2)
        self.assertEqual(record["max_ms"], 9)
        self.assertEqual(record["late_chunks"], 1)
        self.assertIs(record["cache_enabled"], True)

    def test_summarize_lines_tolerates_missing_fields(self) -> None:
        summary = summarize_lines(
            [
                '{"avg_ms": 4.0, "late_chunks": 0, "cache_enabled": true}\n',
                "callback avg_ms=6.0 output_underflows=1 callback_jitter_ms=2.5\n",
                "plain message without metrics\n",
            ]
        )

        self.assertEqual(summary.lines_seen, 3)
        self.assertEqual(summary.records_parsed, 2)
        self.assertIs(summary.flags["cache_enabled"], True)
        self.assertEqual(summary.metrics["avg_ms"].count, 2)
        self.assertEqual(summary.metrics["avg_ms"].average, 5.0)
        self.assertEqual(summary.metrics["late_chunks"].latest, 0)
        self.assertEqual(summary.metrics["output_underflows"].latest, 1)
        self.assertEqual(summary.metrics["callback_jitter_ms"].maximum, 2.5)

    def test_default_summary_behavior_tracks_metrics_and_flags(self) -> None:
        summary = summarize_lines(
            [
                "avg_ms=2.0 max_ms=3.0 cache_enabled=true\n",
                "avg_ms=4.0 max_ms=8.0\n",
            ]
        )

        self.assertEqual(summary.lines_seen, 2)
        self.assertEqual(summary.records_parsed, 2)
        self.assertEqual(summary.metrics["avg_ms"].average, 3.0)
        self.assertEqual(summary.metrics["max_ms"].maximum, 8.0)
        self.assertEqual(summary.flags, {"cache_enabled": True})

    def test_summary_to_csv_includes_metrics_and_flags(self) -> None:
        summary = summarize_lines(
            [
                "avg_ms=2.0 output_underflows=0 cache_enabled=true\n",
                "avg_ms=4.0 output_underflows=1\n",
            ]
        )

        rows = list(csv.DictReader(io.StringIO(summary_to_csv(summary))))
        by_field = {row["field"]: row for row in rows}

        self.assertEqual(by_field["avg_ms"]["count"], "2")
        self.assertEqual(float(by_field["avg_ms"]["average"]), 3.0)
        self.assertEqual(by_field["output_underflows"]["latest"], "1.0")
        self.assertEqual(by_field["cache_enabled"]["value"], "true")

    def test_cli_accepts_csv_format(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(["examples/sample_realtime_log.jsonl", "--format", "csv"])

        self.assertEqual(exit_code, 0)
        self.assertIn("field,count,average", output.getvalue())


if __name__ == "__main__":
    unittest.main()
