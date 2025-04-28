# Run app in Docker
run:
	docker-compose up --build

# Run app on local machine (with local config)
local:
	APP_CONFIG=config/example.toml PYTHONPATH=src python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Run app on local machine (with prod config)
prod:
	APP_CONFIG=config/production.toml PYTHONPATH=src python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

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
	isort .
	flake8 .
	mypy .
