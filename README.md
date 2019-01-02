# philiprehberger-cli-builder

Decorator-based CLI framework with rich output.

## Install

```bash
pip install philiprehberger-cli-builder
```

## Usage

```python
from philiprehberger_cli_builder import CLI, arg, option

cli = CLI(name="myapp", version="1.0.0")

@cli.command()
@arg("name", help="Your name")
@option("--greeting", "-g", default="Hello", help="Greeting to use")
def greet(name: str, greeting: str):
    """Greet someone by name."""
    cli.success(f"{greeting}, {name}!")

@cli.command()
@option("--format", "-f", default="table", choices=["json", "table"])
def status(format: str):
    """Show system status."""
    data = [{"service": "api", "status": "up"}, {"service": "db", "status": "up"}]
    if format == "json":
        cli.json(data)
    else:
        cli.table(data, headers=["Service", "Status"])

cli.run()
```

## Output Helpers

```python
cli.success("Done!")       # ✓ Done!
cli.error("Failed")       # ✗ Failed
cli.warn("Careful")       # ! Careful
cli.info("Note")          # ℹ Note
cli.json(data)            # Pretty-printed JSON
cli.table(data, headers)  # Rich table
cli.progress(items)       # Progress bar
```

## Decorators

| Decorator | Description |
|-----------|-------------|
| `@cli.command()` | Register a command |
| `@arg(name)` | Positional argument |
| `@option(--name, -n)` | Named option with optional short form |

## License

MIT
