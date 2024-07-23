from .index import router as index_page
from .queries import router as queries_page
from .requests import router as requests_page
from .streams import router as streams_page

ALL_ROUTES = (
    index_page,
    queries_page,
    requests_page,
    streams_page,
)
