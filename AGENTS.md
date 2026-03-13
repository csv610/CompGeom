# Repository Guidelines

## Project Structure & Module Organization
Core package code lives under `src/compgeom/`. Major areas are `kernel/` for primitives and predicates, `polygon/` for 2D polygon algorithms, `mesh/` for surface and volumetric mesh logic, `algo/` for general algorithms, `graphics/` for plotting, and `cli/` for command-line entry points. Primary tests live in `tests/` and `src/compgeom/tests/`, with domain-focused suites such as `src/compgeom/tests/polygon/` and `src/compgeom/tests/mesh/`. Documentation and runnable examples are in `docs/`.

## Build, Test, and Development Commands
- `python -m pip install -e .` installs the package in editable mode.
- `pytest -q` runs the full test suite.
- `pytest -q tests/test_polygon_helper_coverage.py` runs a focused regression file.
- `pytest -q src/compgeom/tests/polygon` runs polygon-specific tests.
- `python -m compgeom.cli.main` launches the package CLI entry point.

Use the repo root as the working directory when running commands.

## Coding Style & Naming Conventions
Target Python `>=3.12`. Use 4-space indentation, type hints, and small focused functions. Follow existing naming patterns: `snake_case` for functions/modules, `PascalCase` for classes, and `test_*.py` for test files. Keep public helpers in their domain module unless they are true package-level wrappers. Prefer ASCII unless a file already uses Unicode.

## Testing Guidelines
Tests use `pytest`. Add or update tests with every behavior change, especially for exported helpers in `compgeom.polygon`, `compgeom.mesh`, and CLI parsing code. Name tests by observable behavior, for example `test_polygon_kernel_for_concave_polygon_returns_smaller_region`. Keep broad integration checks in `tests/` and algorithm-specific checks beside the corresponding package test area.

## Commit & Pull Request Guidelines
Recent history uses short imperative subjects such as `feat: ...`, `refactor: ...`, `chore: ...`, or plain action phrases like `Add ...`. Keep commits focused and descriptive. For pull requests, include:
- a brief summary of the behavior change
- test evidence, for example `pytest -q`
- linked issue or rationale when changing algorithms
- screenshots or SVG output only when a visualization or CLI rendering changes

## Contributor Notes
Do not commit generated caches such as `__pycache__/` or `.pytest_cache/`. When moving tests, preserve existing coverage rather than replacing it with broader but weaker assertions.
