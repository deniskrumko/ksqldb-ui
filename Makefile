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

# Run app on local machine (with prod config)
prod:
	PYTHONBREAKPOINT=ipdb.set_trace \
	APP_CONFIG=config/production.toml \
	PYTHONPATH=src \
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# LOCAL DEVELOPMENT
# =================

test:
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
