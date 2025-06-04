from app.core.templates import get_base_context


def test_get_base_context(fastapi_request, init_settings):
    """Should provide all required keys in base context."""
    ctx = get_base_context(fastapi_request)
    assert ctx["current_server"].code == "testing"
    assert not ctx["warning_message"]
    assert ctx["server_query_param"] == "s"
    assert ctx["q"] == "s=testing"
