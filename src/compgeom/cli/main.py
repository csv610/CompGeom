from __future__ import annotations

import argparse
import importlib
import pkgutil
import sys
from collections.abc import Iterable

import compgeom.cli


def _discover_commands() -> dict[str, str]:
    commands: dict[str, str] = {}
    for _, module_name, _ in pkgutil.iter_modules(compgeom.cli.__path__):
        if module_name in {"__init__", "_shared", "main"}:
            continue

        command_name = module_name[:-4] if module_name.endswith("_cli") else module_name
        aliases = {command_name, module_name, f"{command_name}.py"}
        for alias in aliases:
            commands[alias] = module_name
    return commands


def _command_names(commands: dict[str, str]) -> list[str]:
    names: list[str] = []
    for alias, module_name in commands.items():
        canonical_name = module_name[:-4] if module_name.endswith("_cli") else module_name
        if alias == canonical_name:
            names.append(alias)
    return sorted(names)


def _build_parser(command_names: Iterable[str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Computational Geometry CLI")
    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments forwarded to the command")
    parser.epilog = "Available commands: " + ", ".join(command_names)
    return parser


def _resolve_module_name(command: str, commands: dict[str, str]) -> str | None:
    return commands.get(command)


def main(argv: list[str] | None = None) -> int:
    commands = _discover_commands()
    command_names = _command_names(commands)
    parser = _build_parser(command_names)
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    module_name = _resolve_module_name(args.command, commands)
    if module_name is None:
        parser.exit(
            2,
            f"Unknown command: {args.command}\nAvailable commands: {', '.join(command_names)}\n",
        )

    module = importlib.import_module(f"compgeom.cli.{module_name}")
    if not hasattr(module, "main"):
        parser.exit(1, f"Command module {module_name} does not define main().\n")

    sys.argv = [f"{parser.prog} {args.command}", *args.args]
    result = module.main()
    return int(result) if isinstance(result, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
