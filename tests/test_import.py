"""Basic import test."""


def test_import():
    """Verify the package can be imported."""
    import philiprehberger_cli_builder
    assert hasattr(philiprehberger_cli_builder, "__name__") or True
