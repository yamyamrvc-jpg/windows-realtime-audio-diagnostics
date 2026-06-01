"""Print a small Windows audio routing checklist."""

from __future__ import annotations

import argparse


DEVICE_ROUTING_CHECKLIST = """Windows realtime audio device routing notes

Capture devices:
- Note the physical microphone or virtual cable input selected by the app.
- Confirm the Windows default input device is not accidentally overriding app settings.
- Record the sample rate and channel count shown in Windows Sound settings.

Playback devices:
- Note the physical headphones/speakers or virtual cable output selected by the app.
- Disable exclusive-mode conflicts when another app unexpectedly owns the device.
- Keep sample rates consistent across app settings, Windows settings, and virtual cable endpoints.

Virtual routing:
- For VB-CABLE-style routing, remember that CABLE Output is usually selected as an input device by receiving apps.
- CABLE Input is usually selected as a playback device by sending apps.
- Test with a known tone or local recording before debugging application code.

Evidence to collect:
- Device names exactly as shown in Windows.
- App input/output selections.
- Sample rate, channel count, and buffer size.
- Whether underflows, overflows, clipping, or late callbacks appear in logs.
"""


def get_device_routing_checklist() -> str:
    return DEVICE_ROUTING_CHECKLIST


def build_arg_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description="Print Windows realtime audio routing notes.")


def main(argv: list[str] | None = None) -> int:
    build_arg_parser().parse_args(argv)
    print(get_device_routing_checklist())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
