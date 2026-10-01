IMAGE=ksqldb-ui:local
export UV_CACHE_DIR ?= /tmp/uv-cache

# DOCKER COMPOSE
# ==============

# Run app in Docker
up:
	docker-compose up --build -d

# Stop app in Docker
down:
	docker-compose down

logs:
	docker-compose logs ksqldb-ui -f

# DOCKER
# ======

docker-build:
	docker build . -t ${IMAGE} --build-arg KSQLDBUI_VERSION=from-docker

docker-run:
	docker run -p 8080:8080 -v $(PWD)/config:/config --env APP_CONFIG=/config/production.toml ${IMAGE}

# LOCAL RUN
# =========

# Run app on local machine (with local config)
local: compile_translations
	PYTHONBREAKPOINT=ipdb.set_trace \
	APP_CONFIG=config/local.toml \
	PYTHONPATH=src \
	uv run --frozen python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run app using env vars only
usingenv: compile_translations
	PYTHONBREAKPOINT=ipdb.set_trace \
	PYTHONPATH=src \
	KSQLDB_UI__SERVERS__LOCALHOST__URL=http://local.ksqldb \
	KSQLDB_UI__SERVERS__LOCALHOST__NAME=Localhost \
	KSQLDB_UI__SERVERS__PRODUCTION__URL=http://prod.ksqldb \
	KSQLDB_UI__SERVERS__PRODUCTION__DEFAULT=true \
	uv run --frozen python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run app using env vars only
noconfig: compile_translations
	PYTHONBREAKPOINT=ipdb.set_trace \
	PYTHONPATH=src \
	uv run --frozen python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run app on local machine (with prod config)
prod: compile_translations
	PYTHONBREAKPOINT=ipdb.set_trace \
	APP_CONFIG=config/production.toml \
	PYTHONPATH=src \
	uv run --frozen python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# LOCAL DEVELOPMENT
# =================

# Install all dependencies
deps: vendor uv-sync

# Install Python dependencies
uv-sync:
	uv sync --frozen

# Install vendor libraries
vendor:
	VENDOR=src/static/vendor sh scripts/download_vendor.sh

# Collect i18n translation stirngs
collect_translations:
	./scripts/collect_translations.sh

# Compile i18n translations
compile_translations:
	./scripts/compile_translations.sh

find_missing_translations:
	./scripts/find_missing_translations.sh
	@echo "✅  Translation checked"

# Open ksqldb UI
ui:
	open http://localhost:8080

# Run tests
tests:
	PYTHONPATH=src uv run --frozen pytest --cov

# Run tests with coverage
coverage:
	PYTHONPATH=src uv run --frozen pytest --cov --cov-report=html:htmlcov --disable-warnings || true
	open htmlcov/index.html

# Formatting
fmt:
	@uv run ruff format .
	@uv run ruff check --fix .
	@echo "✅  Code formatted"

# Linting
lint:
	@uv run ruff format --check . || (echo "Ruff format check failed. Run make fmt" && exit 1)
	@uv run ruff check .
	@echo "✅  Lint checks passed"
	@uv run ty check .
	@echo "✅  Type check passed"

# Check translations in extraction, completeness, and compilation order
translations_check: collect_translations find_missing_translations compile_translations

# Run all checks
check: translations_check fmt lint tests
