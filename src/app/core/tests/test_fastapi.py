import asyncio

from app.core.fastapi import CacheControlledStaticFiles


def test_cache_control_header(tmp_path):
    """Should set Cache-Control header on static file response."""
    static_dir = tmp_path
    (static_dir / "foo.txt").write_text("bar")
    app = CacheControlledStaticFiles(directory=static_dir, max_age=123)
    scope = {"type": "http", "path": "/foo.txt", "method": "GET", "headers": []}
    response = asyncio.run(app.get_response("foo.txt", scope))
    assert response.headers["Cache-Control"] == "public, max-age=123"
