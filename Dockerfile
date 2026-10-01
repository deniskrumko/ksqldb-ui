FROM debian:bookworm-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.28 /uv /usr/local/bin/uv
COPY --from=ghcr.io/astral-sh/uv:0.11.28 /uvx /usr/local/bin/uvx

ENV UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_PYTHON=3.14.6 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:/usr/local/bin:/usr/bin:/bin"

RUN uv python install 3.14.6

RUN mkdir build
WORKDIR /build

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies from the committed lockfile.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Install JS/CSS vendor dependencies
COPY ./ .
RUN set -e && \
    VENDOR=src/static/vendor sh scripts/download_vendor.sh

# Compile translations
RUN sh scripts/compile_translations.sh

ARG KSQLDBUI_VERSION="undefined"
RUN echo ${KSQLDBUI_VERSION} >> .version

ENV PYTHONPATH=src
EXPOSE 8080

CMD ["uv", "run", "--no-sync", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
