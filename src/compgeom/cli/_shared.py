from __future__ import annotations

import sys
from typing import Iterable


def read_stdin_lines() -> list[str]:
    return sys.stdin.readlines()


def read_nonempty_stdin_lines() -> list[str]:
    return [line.strip() for line in sys.stdin if line.strip()]


def print_lines(lines: Iterable[str]) -> None:
    for line in lines:
        print(line)
