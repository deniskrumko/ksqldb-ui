FROM python:3.12.11-slim-bullseye

RUN mkdir build
WORKDIR /build

# Install dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install python packages
RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --ignore-pipfile --system && \
    pip uninstall -y pipenv && \
    rm -rf ~/.cache/pip /root/.cache/pipenv /root/.local/share/virtualenvs

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
