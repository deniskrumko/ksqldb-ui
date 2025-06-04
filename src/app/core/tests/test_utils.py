from app.core.utils import (
    flatten_dict,
    make_list,
)


def test_make_list_with_list():
    """Should return the same list if input is already a list."""
    assert make_list([1, 2, 3]) == [1, 2, 3]


def test_make_list_with_scalar():
    """Should wrap a scalar value in a list."""
    assert make_list(42) == [42]
    assert make_list("foo") == ["foo"]


def test_flatten_dict_simple():
    """Should flatten a simple nested dictionary."""
    d = {"a": {"b": 1}}
    assert flatten_dict(d) == {"a.b": 1}


def test_flatten_dict_deep():
    """Should flatten a deeply nested dictionary."""
    d = {"a": {"b": {"c": 2}}}
    assert flatten_dict(d) == {"a.b.c": 2}


def test_flatten_dict_with_sep():
    """Should use custom separator when provided."""
    d = {"a": {"b": 1}}
    assert flatten_dict(d, sep="_") == {"a_b": 1}
