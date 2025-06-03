from os import getenv
from typing import (
    Mapping,
    Optional,
)

from dynaconf import Dynaconf
from fastapi import Request
from pydantic import BaseModel

from .urls import SimpleURL

SERVER_QUERY_PARAM: str = "s"
README = "https://github.com/deniskrumko/ksqldb-ui/blob/master/README.md"


class HTTPSettings(BaseModel):
    timeout: int = 5


class Server(BaseModel):
    code: str
    url: str
    name: str | None = None
    default: bool = False
    topic_link: str | None = None
    warning_message: str | None = None

    def __str__(self) -> str:
        return self.code.lower().replace("_", "-")

    def __repr__(self) -> str:
        return f"<Server: {self.name}>"

    @property
    def display_name(self) -> str:
        return self.name or self.code.title()

    @property
    def simple_url(self) -> SimpleURL:
        return SimpleURL(self.url)

    @property
    def queue(self) -> str:
        return f"{SERVER_QUERY_PARAM}={self.code}"


class HistorySettings(BaseModel):
    enabled: bool = True
    size: int = 50


class Settings(BaseModel):
    http: HTTPSettings
    history: HistorySettings
    servers: dict[str, Server]

    @property
    def default_server(self) -> Server:
        """Get default server if it's defined. Otherwise get last."""
        for server in self.servers.values():
            if server.default:
                return server

        return server

    def get_server(self, code: str) -> Server:
        try:
            return self.servers[code]
        except KeyError:
            raise ValueError(f'Server "{code}" is not found to config file')

    @classmethod
    def from_config(cls, config: Mapping) -> "Settings":
        settings = cls(
            http=HTTPSettings(**config.get("http", {})),
            history=HistorySettings(**config.get("history", {})),
            servers={
                code: Server(code=code, **params)
                for code, params in config.get("servers", {}).items()
            },
        )

        if not settings.servers:
            raise ValueError(
                "At least one ksqlDB server must be added to config file or using env variables",
            )

        return settings


SETTINGS: Optional[Settings] = None


def get_settings() -> Settings:
    """Get settings from .toml file or env vars."""
    global SETTINGS

    if SETTINGS is not None:
        return SETTINGS

    settings = Settings.from_config(
        Dynaconf(
            envvar_prefix="KSQLDB_UI_",
            settings_file=getenv("APP_CONFIG"),
        ),
    )

    SETTINGS = settings
    return settings


def get_server(request: Request) -> Server:
    """Get current server from request."""
    code = get_server_code(request)
    settings = get_settings()
    return settings.get_server(code)


def get_server_code(request: Request, raise_exc: bool = True) -> str:
    """Get current server code from request."""
    try:
        return request.query_params[SERVER_QUERY_PARAM]
    except KeyError:
        if not raise_exc:
            return ""

        raise ValueError(f"{SERVER_QUERY_PARAM} query param is not defined")
