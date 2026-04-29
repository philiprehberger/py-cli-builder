"""Tests for philiprehberger_cli_builder."""

from __future__ import annotations

import pytest

from philiprehberger_cli_builder import CLI, arg, option


def test_single_command_no_args(capsys: pytest.CaptureFixture[str]) -> None:
    cli = CLI(name="t")
    called: list[bool] = []

    @cli.command()
    def hello() -> None:
        called.append(True)

    cli.run([])
    assert called == [True]


def test_command_with_positional_arg() -> None:
    cli = CLI(name="t")
    captured: dict[str, str] = {}

    @cli.command()
    @arg("name", help="user name")
    def greet(name: str) -> None:
        captured["name"] = name

    cli.run(["alice"])
    assert captured["name"] == "alice"


def test_command_with_option() -> None:
    cli = CLI(name="t")
    captured: dict[str, str] = {}

    @cli.command()
    @option("--prefix", default="Hi")
    def greet(prefix: str = "Hi") -> None:
        captured["prefix"] = prefix

    cli.run(["--prefix", "Hello"])
    assert captured["prefix"] == "Hello"


def test_command_with_flag() -> None:
    cli = CLI(name="t")
    captured: dict[str, bool] = {}

    @cli.command()
    @option("--verbose", is_flag=True)
    def run(verbose: bool = False) -> None:
        captured["verbose"] = verbose

    cli.run(["--verbose"])
    assert captured["verbose"] is True


def test_subcommand_dispatch() -> None:
    cli = CLI(name="t")
    seen: list[str] = []

    @cli.command()
    def alpha() -> None:
        seen.append("alpha")

    @cli.command()
    def beta() -> None:
        seen.append("beta")

    cli.run(["beta"])
    assert seen == ["beta"]


def test_command_aliases() -> None:
    cli = CLI(name="t")
    seen: list[str] = []

    @cli.command(name="list", aliases=["ls", "l"])
    def list_things() -> None:
        seen.append("list")

    @cli.command()
    def other() -> None:
        seen.append("other")

    cli.run(["ls"])
    cli.run(["l"])
    cli.run(["list"])
    assert seen == ["list", "list", "list"]


def test_alias_resolves_to_same_command() -> None:
    cli = CLI(name="t")

    @cli.command(name="install", aliases=["i"])
    def install() -> None:
        pass

    cmd = cli._resolve_command("i")
    assert cmd.name == "install"


def test_help_when_no_command(capsys: pytest.CaptureFixture[str]) -> None:
    cli = CLI(name="t")

    @cli.command()
    def alpha() -> None:
        pass

    @cli.command()
    def beta() -> None:
        pass

    cli.run([])
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_typed_option_is_cast() -> None:
    cli = CLI(name="t")
    captured: dict[str, int] = {}

    @cli.command()
    @option("--count", type=int, default=1)
    def go(count: int = 1) -> None:
        captured["count"] = count

    cli.run(["--count", "5"])
    assert captured["count"] == 5
    assert isinstance(captured["count"], int)


def test_output_helpers_do_not_raise() -> None:
    cli = CLI(name="t")
    cli.success("ok")
    cli.error("bad")
    cli.warn("careful")
    cli.info("info")
    cli.json({"a": 1, "b": [2, 3]})
    cli.table([{"x": 1, "y": 2}, {"x": 3, "y": 4}])
