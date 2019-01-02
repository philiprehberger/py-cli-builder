"""Decorator-based CLI framework with rich output."""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, get_type_hints

from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.json import JSON

__all__ = ["CLI", "arg", "option"]

_console = Console()


@dataclass
class _ArgDef:
    name: str
    help: str | None = None
    type: type | None = None
    default: Any = None
    required: bool = True
    nargs: str | None = None


@dataclass
class _OptionDef:
    name: str
    short: str | None = None
    help: str | None = None
    type: type | None = None
    default: Any = None
    choices: list[str] | None = None
    is_flag: bool = False


_ARG_ATTR = "__cli_args__"
_OPT_ATTR = "__cli_options__"


def arg(name: str, help: str | None = None, type: type | None = None) -> Callable:
    """Decorator to define a positional argument."""
    def decorator(fn: Callable) -> Callable:
        args = getattr(fn, _ARG_ATTR, [])
        args.append(_ArgDef(name=name, help=help, type=type))
        setattr(fn, _ARG_ATTR, args)
        return fn
    return decorator


def option(
    name: str,
    short: str | None = None,
    help: str | None = None,
    default: Any = None,
    choices: list[str] | None = None,
    is_flag: bool = False,
) -> Callable:
    """Decorator to define a command option."""
    def decorator(fn: Callable) -> Callable:
        opts = getattr(fn, _OPT_ATTR, [])
        opts.append(_OptionDef(
            name=name, short=short, help=help,
            default=default, choices=choices, is_flag=is_flag,
        ))
        setattr(fn, _OPT_ATTR, opts)
        return fn
    return decorator


@dataclass
class _Command:
    name: str
    fn: Callable
    help: str | None
    args: list[_ArgDef]
    options: list[_OptionDef]


class CLI:
    """Decorator-based CLI framework."""

    def __init__(
        self,
        name: str = "cli",
        version: str | None = None,
        description: str | None = None,
    ) -> None:
        self.name = name
        self.version = version
        self.description = description
        self._commands: dict[str, _Command] = {}
        self._console = _console

    def command(self, name: str | None = None) -> Callable:
        """Decorator to register a command."""
        def decorator(fn: Callable) -> Callable:
            cmd_name = name or fn.__name__
            args = list(reversed(getattr(fn, _ARG_ATTR, [])))
            opts = list(reversed(getattr(fn, _OPT_ATTR, [])))
            cmd = _Command(
                name=cmd_name,
                fn=fn,
                help=fn.__doc__,
                args=args,
                options=opts,
            )
            self._commands[cmd_name] = cmd
            return fn
        return decorator

    def run(self, args: list[str] | None = None) -> None:
        """Parse arguments and run the appropriate command."""
        parser = argparse.ArgumentParser(
            prog=self.name,
            description=self.description,
        )

        if self.version:
            parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        if len(self._commands) == 1:
            # Single command — no subcommands
            cmd = next(iter(self._commands.values()))
            self._add_command_args(parser, cmd)
            parsed = parser.parse_args(args)
            self._run_command(cmd, parsed)
        else:
            subparsers = parser.add_subparsers(dest="_command")
            for cmd in self._commands.values():
                sub = subparsers.add_parser(cmd.name, help=cmd.help)
                self._add_command_args(sub, cmd)

            parsed = parser.parse_args(args)
            cmd_name = getattr(parsed, "_command", None)
            if not cmd_name:
                parser.print_help()
                return

            cmd = self._commands[cmd_name]
            self._run_command(cmd, parsed)

    def _add_command_args(self, parser: argparse.ArgumentParser, cmd: _Command) -> None:
        for a in cmd.args:
            kwargs: dict[str, Any] = {}
            if a.help:
                kwargs["help"] = a.help
            if a.type:
                kwargs["type"] = a.type
            parser.add_argument(a.name, **kwargs)

        for o in cmd.options:
            names = [o.name]
            if o.short:
                names.insert(0, o.short)

            kwargs = {}
            if o.help:
                kwargs["help"] = o.help
            if o.choices:
                kwargs["choices"] = o.choices
            if o.is_flag:
                kwargs["action"] = "store_true"
                kwargs["default"] = o.default or False
            else:
                kwargs["default"] = o.default
                if o.type:
                    kwargs["type"] = o.type

            dest = o.name.lstrip("-").replace("-", "_")
            kwargs["dest"] = dest
            parser.add_argument(*names, **kwargs)

    def _run_command(self, cmd: _Command, parsed: argparse.Namespace) -> None:
        sig = inspect.signature(cmd.fn)
        kwargs: dict[str, Any] = {}
        for param_name in sig.parameters:
            if hasattr(parsed, param_name):
                kwargs[param_name] = getattr(parsed, param_name)
        try:
            cmd.fn(**kwargs)
        except KeyboardInterrupt:
            self._console.print("\n[dim]Interrupted.[/dim]")
        except Exception as e:
            self.error(str(e))
            sys.exit(1)

    # --- Output helpers ---

    def success(self, message: str) -> None:
        """Print a success message."""
        self._console.print(f"[green]✓[/green] {message}")

    def error(self, message: str) -> None:
        """Print an error message."""
        self._console.print(f"[red]✗[/red] {message}", style="red")

    def warn(self, message: str) -> None:
        """Print a warning message."""
        self._console.print(f"[yellow]![/yellow] {message}")

    def info(self, message: str) -> None:
        """Print an info message."""
        self._console.print(f"[blue]ℹ[/blue] {message}")

    def json(self, data: Any) -> None:
        """Pretty-print JSON data."""
        self._console.print(JSON(json.dumps(data, indent=2, default=str)))

    def table(
        self,
        data: list[dict] | list[list],
        headers: list[str] | None = None,
        title: str | None = None,
    ) -> None:
        """Print data as a table."""
        t = Table(title=title)
        if headers:
            for h in headers:
                t.add_column(h)
        elif data and isinstance(data[0], dict):
            headers = list(data[0].keys())
            for h in headers:
                t.add_column(h)

        for row in data:
            if isinstance(row, dict):
                t.add_row(*[str(v) for v in row.values()])
            else:
                t.add_row(*[str(v) for v in row])

        self._console.print(t)

    @staticmethod
    def progress(iterable: Any, description: str = "Processing...") -> Any:
        """Wrap an iterable with a progress bar."""
        return track(iterable, description=description)
