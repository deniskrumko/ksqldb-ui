![ksqldb-ui](https://github.com/deniskrumko/ksqldb-ui/blob/main/src/static/images/full_logo_readme.png?raw=true)

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/deniskrumko/ksqldb-ui/build-and-push.yml)](https://github.com/deniskrumko/ksqldb-ui/actions)
[![GitHub Release](https://img.shields.io/github/v/release/deniskrumko/ksqldb-ui)](https://github.com/deniskrumko/ksqldb-ui/releases)
[![Docker pulls](https://img.shields.io/docker/pulls/deniskrumko/ksqldb-ui)](https://hub.docker.com/r/deniskrumko/ksqldb-ui/tags)

A web UI for [ksqlDB](https://ksqldb.io/). Send requests and interact with queries and streams in a browser instead of using the CLI. Built with Python, FastAPI, and Jinja2.

Check out the image on Docker Hub: https://hub.docker.com/r/deniskrumko/ksqldb-ui

![preview](https://github.com/deniskrumko/ksqldb-ui/blob/main/src/static/images/preview.png?raw=true)

# Features

- Write requests to manage streams and queries in the UI
- View existing queries and streams along with detailed information
- View the topology of streams and queries (how data flows between streams)
- Delete existing queries and streams
- Pause and resume queries
- Use the UI in English (the default) or Russian

# How it works

You can deploy your ksqlDB server in either [interactive or headless mode](https://docs.confluent.io/platform/current/ksqldb/operate-and-deploy/how-it-works.html#ksqldb-deployment-modes).

ksqlDB UI works only with servers in **interactive mode**, which allows it to manage the ksqlDB server through the [REST API](https://docs.ksqldb.io/en/latest/developer-guide/api/).

All available ksqlDB statements [are listed in the documentation](https://docs.ksqldb.io/en/latest/developer-guide/ksqldb-reference/quick-reference/).

## Limitations

- You can't use the `RUN SCRIPT` statement in this UI because [it requires a file](https://docs.ksqldb.io/en/latest/developer-guide/ksqldb-reference/run-script/)
- [Authentication is not yet supported](https://github.com/deniskrumko/ksqldb-ui/issues/6)

# How to use ksqlDB UI

**Note:** For production deployments, use a specific version from the [available tags](https://hub.docker.com/r/deniskrumko/ksqldb-ui/tags) instead of `deniskrumko/ksqldb-ui:latest`.

## Using Docker

```bash
# Download the image
docker pull deniskrumko/ksqldb-ui:latest

# Run the container
# Create a config/production.toml file in the current directory first
docker run \
    -p 8080:8080 \
    -v $(PWD)/config:/config \
    --env APP_CONFIG=/config/production.toml \
    deniskrumko/ksqldb-ui:latest
```

## Using docker-compose.yml

1. Create a `docker-compose.yml` file:

```yaml
services:
  ksqldb-ui:
    image: deniskrumko/ksqldb-ui:latest
    environment:
      APP_CONFIG: /config.toml
    volumes:
      - ./development.toml:/config.toml
    ports:
      - 8080:8080
```

2. Run `docker-compose up -d`.

3. Open your browser and navigate to http://localhost:8080.

See the working example of ksqlDB and ksqlDB UI below.

## Using Kubernetes manifests

**deployment.yml**:

```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ksqldb-ui
  namespace: development
  labels: &labels
    your-labels-here: ksqldb-ui
spec:
  progressDeadlineSeconds: 300
  selector:
    matchLabels: *labels
  replicas: 1
  template:
    metadata:
      labels: *labels
    spec:
      volumes:
        - name: config
          configMap:
            name: ksqldb-ui-configmap
      containers:
        - name: ksqldb-ui
          image: deniskrumko/ksqldb-ui:latest
          volumeMounts:
          - name: config
            mountPath: /config/config.toml
            subPath: config.toml
          ports:
            - containerPort: 8080
          env:
            - name: APP_CONFIG
              value: /config/config.toml
          resources:
            limits:
              cpu: "1"
              memory: 128Mi
            requests:
              cpu: "0.1"
              memory: 64Mi
```

**configmap.yml**:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ksqldb-ui-configmap
  namespace: development
  labels:
    your-labels-here: ksqldb-ui
data:
  config.toml: |
    [servers.development]
    url = 'http://your-development-ksqldb.com'
    topic_link = 'http://your-development-kafka-ui.com/topics/{}'

    [servers.production]
    url = 'http://your-production-ksqldb.com'
    topic_link = 'http://your-production-kafka-ui.com/topics/{}'
```

You can create any additional manifests (such as `ingress.yml`) yourself 👌

# Configuration

## Using a `.toml` file and the `APP_CONFIG` environment variable

See the example configuration file: [config/example.toml](./config/example.toml).

To run ksqlDB UI, create your own configuration file and set the `APP_CONFIG` environment variable to its path. See the "How to use ksqlDB UI" section above.

The simplest possible configuration:

```toml
[servers.localhost]
url = "http://localhost:8090"
```

Full configuration documentation is planned for a future update.

## Using only environment variables

ksqlDB UI uses [Dynaconf](https://www.dynaconf.com/) for configuration, so **all settings** can be defined or overridden using environment variables. Follow these rules:

- Add the `KSQLDB_UI__` prefix to each variable
- Separate nested parameters with double underscores: `__`
- Use uppercase names for environment variables

For example, the following `config.toml` settings:

```toml
[http]
timeout = 60

[servers.localhost]
url = 'http://localhost:8080'

[servers.production]
url = 'http://production:8080'
filters = [['Alice', 'Bob'], ['Red', 'Green', 'Yellow']]
```

can be replaced with these environment variables:

```bash
KSQLDB_UI__HTTP__TIMEOUT=60
KSQLDB_UI__SERVERS__LOCALHOST__URL=http://localhost:8080
KSQLDB_UI__SERVERS__PRODUCTION__URL=http://production:8080
KSQLDB_UI__SERVERS__PRODUCTION__FILTERS="[['Alice', 'Bob'], ['Red', 'Green', 'Yellow']]"
```

Notes:

- The `APP_CONFIG` environment variable is not required when using `KSQLDB_UI__` environment variables, but you can use both
- `KSQLDB_UI__` environment variables **always override** settings from the file specified by `APP_CONFIG`
- You can also view all available environment variables on the `/debug` page in ksqlDB UI

# Working example

The [docker-compose.yml](./docker-compose.yml) example includes four components:

- ksqldb
- ksqldb-ui
- Redpanda (like Apache Kafka, but better 😎)
- Redpanda UI

To run this example:

1. Download [docker-compose.yml](./docker-compose.yml) to your machine.

2. Run the following command:

```bash
docker-compose up -d
```

3. Open ksqlDB UI at http://localhost:8080 in your browser to create streams and queries.

4. Open Redpanda UI at http://localhost:8090 in your browser to create topics.

# API

**Note:** All API requests must specify a server using the `?s=<server_code>` query parameter.

## POST `/api/request`

Proxy a request to the ksqlDB server.

The response status code is always **HTTP 200** (unless an error occurs in ksqlDB UI). This means that ksqlDB UI received a response from the ksqlDB server. To check for ksqlDB errors, inspect the `success` and `data.response` fields in the response body.

```bash
curl http://localhost:8080/api/request?s=dev \
    -d "{
        \"query\": \"list streamzzz\"
    }"
```

Error response (because the query is invalid):

```json
{
  "success": false,
  "data": {
    "query": "list streamzzz",
    "response": {
      "@type": "statement_error",
      "error_code": 40001,
      "message": "line 1:6: Syntax Error\nSyntax error at or near 'streamzzz' at line 1:6",
      "statementText": "list streamzzz;",
      "entities": []
    }
  }
}
```

## POST `/api/process_file`

Upload a file containing SQL statements and receive a response.

The response status code is always **HTTP 200** (unless an error occurs in ksqlDB UI). This means that ksqlDB UI received a response from the ksqlDB server. To check for ksqlDB errors, inspect the `success` and `data.response` fields in the response body.

Request using a `request.sql` file:

```bash
curl -F "file=@./request.sql" http://localhost:8080/api/process_file?s=dev
```

File contents:

```sql
list streams;
```

Response:

```json
{
  "success": true,
  "data": {
    "query": "list streams;",
    "response": [
      {
        "@type": "streams",
        "statementText": "list streams;",
        "streams": [
          {
            "type": "STREAM",
            "name": "MY_COOL_STREAM",
            "topic": "my-cool-stream",
            "keyFormat": "JSON_SR",
            "valueFormat": "JSON_SR",
            "isWindowed": false
          }
        ],
        "warnings": []
      }
    ]
  }
}
```

# Credits

- Powered by Python 3.14, FastAPI, and Jinja2
- UI built with [Bootstrap 5.3](https://getbootstrap.com/docs/5.3/)
- SQL editor powered by [Ace](https://ace.c9.io/)
- Icons from [Google Fonts](https://fonts.google.com/icons?icon.size=24&icon.color=%23e3e3e3)
- Markdown tables from [tablesgenerator.com](https://www.tablesgenerator.com/markdown_tables)
