from fastapi import (
    FastAPI,
    Request,
)
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
from pathlib import Path

app = FastAPI()
templates_dir = Path(__file__).parent.parent / 'templates'
templates = Jinja2Templates(directory=templates_dir)


@app.get("/")
async def root(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(
        'index.html',
        context={'request': request},
    )
