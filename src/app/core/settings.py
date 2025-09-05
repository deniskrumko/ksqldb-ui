from os import getenv
from typing import (
    Any,
    Mapping,
    Optional,
)

import pydantic
from dynaconf import Dynaconf
from fastapi import Request
from pydantic import BaseModel

from .urls import SimpleURL
from .utils import flatten_dict

ENV_VAR_PREFIX = "KSQLDB_UI"
SERVER_QUERY_PARAM: str = "s"
README = "https://github.com/deniskrumko/ksqldb-ui/blob/master/README.md"


class LowercaseKeyMixin:
    """Mixin to normalize keys to lowercase before validation."""

    @pydantic.model_validator(mode="before")
    def normalize_keys(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {k.lower(): v for k, v in data.items()}


class HTTPSettings(LowercaseKeyMixin, BaseModel):
    """HTTP settings for the app."""

    timeout: int = 5


class Server(LowercaseKeyMixin, BaseModel):
    """Server configuration model."""

    code: str
    url: str
    name: str | None = None
    default: bool = False
    filters: list[list[str]] | None = None
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
    def query(self) -> str:
        return f"{SERVER_QUERY_PARAM}={self.code}"


class HistorySettings(LowercaseKeyMixin, BaseModel):
    """Settings for requests history."""

    enabled: bool = True
    size: int = 50


class CustomTemplate(LowercaseKeyMixin, BaseModel):
    """Custom template model."""

    envs: list[str] | None = None
    type: str | None = None
    description: str
    query: str


class TemplatesSettings(LowercaseKeyMixin, BaseModel):
    """Settings for templates."""

    show_builtin_templates: bool = True
    custom: dict[str, CustomTemplate] = {}


class GlobalSettings(LowercaseKeyMixin, BaseModel):
    """Global settings for the app."""

    language: str = "en"  # Default language
    show_hints: bool = True  # Show hints in UI
    branding: str = "ksqldb-ui"  # Branding text
    display_version: bool = True  # Display app version in UI


class Settings(BaseModel):
    """App settings."""

    http: HTTPSettings
    history: HistorySettings
    templates: TemplatesSettings
    servers: dict[str, Server]
    global_settings: GlobalSettings

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
            templates=TemplatesSettings(**config.get("templates", {})),
            global_settings=GlobalSettings(**config.get("global", {})),
            servers={
                code.lower(): Server(code=code.lower(), **params)
                for code, params in config.get("servers", {}).items()
            },
        )

        if not settings.servers:
            raise ValueError(
                "At least one ksqlDB server must be added to config file or using env variables",
            )

        return settings

    @property
    def as_flatten_dict(self) -> dict:
        data = self.model_dump()
        for server in data["servers"].values():
            server.pop("code")  # internal field

        return flatten_dict(data)

    @property
    def avaiable_env_vars(self) -> list[str]:
        return [
            f"{ENV_VAR_PREFIX}__{key.replace('.', '__').upper()}" for key in self.as_flatten_dict
        ]

    @property
    def sorted_servers(self) -> list[Server]:
        return sorted(self.servers.values(), key=lambda x: x.code)


SETTINGS: Optional[Settings] = None


def init_settings(settings: Settings) -> None:
    if not isinstance(settings, Settings):
        raise TypeError("Settings must be <Settings> instance")

    global SETTINGS
    SETTINGS = settings


def get_settings() -> Settings:
    """Get settings from .toml file or env vars."""
    if SETTINGS is not None:
        return SETTINGS

    settings = Settings.from_config(
        Dynaconf(
            envvar_prefix=ENV_VAR_PREFIX + "_",
            settings_file=getenv("APP_CONFIG"),
        ),
    )

    init_settings(settings)
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
