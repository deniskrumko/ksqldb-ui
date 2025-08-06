IMAGE=ksqldb-ui:local

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
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run app using env vars only
usingenv: compile_translations
	PYTHONBREAKPOINT=ipdb.set_trace \
	PYTHONPATH=src \
	KSQLDB_UI__SERVERS__LOCALHOST__URL=http://local.ksqldb \
	KSQLDB_UI__SERVERS__LOCALHOST__NAME=Localhost \
	KSQLDB_UI__SERVERS__PRODUCTION__URL=http://prod.ksqldb \
	KSQLDB_UI__SERVERS__PRODUCTION__DEFAULT=true \
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run app using env vars only
noconfig: compile_translations
	PYTHONBREAKPOINT=ipdb.set_trace \
	PYTHONPATH=src \
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run app on local machine (with prod config)
prod: compile_translations
	PYTHONBREAKPOINT=ipdb.set_trace \
	APP_CONFIG=config/production.toml \
	PYTHONPATH=src \
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# LOCAL DEVELOPMENT
# =================

# Install all dependencies
deps: vendor pipenv

# Install py dependencies
pipenv:
	pip install pipenv
	pipenv install --dev

# Install vendor libraries
vendor:
	VENDOR=src/static/vendor sh scripts/download_vendor.sh

# Collect i18n translation stirngs
collect_translations:
	./scripts/collect_translations.sh

# Compile i18n translations
compile_translations:
	./scripts/compile_translations.sh

# Open ksqldb UI
ui:
	open http://localhost:8080

# Run tests
tests:
	PYTHONPATH=src pytest --cov

# Run tests with coverage
coverage:
	PYTHONPATH=src pytest --cov --cov-report=html:htmlcov --disable-warnings || true
	open htmlcov/index.html

# Formatting
fmt:
	black .
	isort .

# Linting
lint:
	flake8 .
	mypy .

# Run all checks
check: fmt lint tests
