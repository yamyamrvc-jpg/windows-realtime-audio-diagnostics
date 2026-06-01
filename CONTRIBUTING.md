# Contributing

Thanks for considering a contribution.

## Scope

This project is a generic diagnostics toolkit for Windows realtime audio development. Contributions should stay within that scope.

Please do not contribute:

- Voice conversion code.
- Model inference code.
- GPU backend code.
- Proprietary realtime engine internals.
- Ring-buffer, de-click, or private scheduling algorithms copied from another project.
- Logs or audio files containing private user data.

## Development

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## Style

- Keep modules small and readable.
- Prefer typed public functions.
- Add tests for behavior changes.
- Keep fixtures anonymous and synthetic.
- Favor generic Windows audio terminology over product-specific assumptions.

## Pull Requests

Include a short description, test results, and any limitations. If a change adds parsing support for a new log format, include a small anonymous sample in the tests.
