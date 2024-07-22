from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import RedirectResponse

router = APIRouter()
PAGE_TEMPLATE = 'index.html'


@router.get("/", response_class=RedirectResponse)
async def index_page(request: Request) -> str:
    return '/requests'
