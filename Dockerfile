FROM python:3.12.4-slim-bullseye

RUN mkdir build
WORKDIR /build

# Install dependencies
RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --ignore-pipfile --system

COPY src/ .
EXPOSE 8080

CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
