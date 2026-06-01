from __future__ import annotations

import unittest

from wrad.log_summary import parse_log_line, summarize_lines


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


if __name__ == "__main__":
    unittest.main()
