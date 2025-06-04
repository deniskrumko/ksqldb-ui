from app.core.render import (
    RENDER_HELPERS,
    register,
)


def test_register_decorator():
    """Should register a function in RENDER_HELPERS."""

    @register
    def foo(x):
        return x + 1

    assert "foo" in RENDER_HELPERS
    assert RENDER_HELPERS["foo"](2) == 3
