FROM python:3.12.11-slim-bullseye

COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /uvx

RUN mkdir build
WORKDIR /build

# Install dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies from the committed lockfile.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --system

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

CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
