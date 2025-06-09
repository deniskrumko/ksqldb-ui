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

# LOCAL RUN
# =========

# Run app on local machine (with local config)
local:
	PYTHONBREAKPOINT=ipdb.set_trace \
	APP_CONFIG=config/local.toml \
	PYTHONPATH=src \
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run app using env vars only
usingenv:
	PYTHONBREAKPOINT=ipdb.set_trace \
	PYTHONPATH=src \
	KSQLDB_UI__SERVERS__LOCALHOST__URL=http://local.ksqldb \
	KSQLDB_UI__SERVERS__LOCALHOST__NAME=Localhost \
	KSQLDB_UI__SERVERS__PRODUCTION__URL=http://prod.ksqldb \
	KSQLDB_UI__SERVERS__PRODUCTION__DEFAULT=true \
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run app using env vars only
noconfig:
	PYTHONBREAKPOINT=ipdb.set_trace \
	PYTHONPATH=src \
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run app on local machine (with prod config)
prod:
	PYTHONBREAKPOINT=ipdb.set_trace \
	APP_CONFIG=config/production.toml \
	PYTHONPATH=src \
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# LOCAL DEVELOPMENT
# =================

tests:
	PYTHONPATH=src pytest

# Open UI
ui:
	open http://localhost:8080

# Install deps
deps:
	pip install pipenv
	pipenv install --dev

check:
	black .
	isort .
	flake8 .
	mypy .
	@$(MAKE) tests
