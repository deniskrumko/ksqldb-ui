FROM python:3.12.4-slim-bullseye

RUN mkdir build
WORKDIR /build

# Install dependencies
RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --ignore-pipfile --system

COPY src/ .
WORKDIR /build/app
EXPOSE 8080

CMD python -m uvicorn main:app --host 0.0.0.0 --port 8080
