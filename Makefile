# Run app in Docker
run:
	docker-compose up --build

# Run app on local machine
local:
	PYTHONPATH=src python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Open UI
ui:
	open http://localhost:8080

# Install deps
deps:
	pip install pipenv
	pipenv install --dev

lint:
	isort .
	flake8 .
	mypy .
