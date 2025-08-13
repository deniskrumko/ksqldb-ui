![ksqldb-ui](https://github.com/deniskrumko/ksqldb-ui/blob/main/src/static/images/full_logo_readme.png?raw=true)

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/deniskrumko/ksqldb-ui/build-and-push.yml)](https://github.com/deniskrumko/visual-coordinates-tool/actions)
[![GitHub Release](https://img.shields.io/github/v/release/deniskrumko/ksqldb-ui)](https://github.com/deniskrumko/ksqldb-ui/releases)
[![Docker pulls](https://img.shields.io/docker/pulls/deniskrumko/ksqldb-ui)](https://hub.docker.com/r/deniskrumko/ksqldb-ui/tags)

Web UI for [ksqlDB](https://ksqldb.io/). Make requests and interact with queries or streams using browser instead of CLI. Written on Python, FastAPI and Jinja2.

Checkout image on Docker Hub: https://hub.docker.com/r/deniskrumko/ksqldb-ui

![preview](https://github.com/deniskrumko/ksqldb-ui/blob/main/src/static/images/preview.png?raw=true)

# Features

- Write requests to manipulate streams/queries in UI
- View list of existing queries/streams and detailed info
- View stream/queries topology (how data flows from stream to stream)
- Delete existing queries/streams
- Has translated UI - English (by default), Russian

# How it works

You can deploy your ksqlDB server using either [Interactive or Headless mode](https://docs.confluent.io/platform/current/ksqldb/operate-and-deploy/how-it-works.html#ksqldb-deployment-modes)

KsqlDB UI works only for servers in **Interactive mode** because it allows to use [REST API](https://docs.ksqldb.io/en/latest/developer-guide/api/) to manipulate ksqlDB server

All statements that exist in ksqlDB [are listed in their documentation](https://docs.ksqldb.io/en/latest/developer-guide/ksqldb-reference/quick-reference/)

## Limitations

- You can't use `RUN SCRIPT` statement in this UI because [it can only be executed using file](https://docs.ksqldb.io/en/latest/developer-guide/ksqldb-reference/run-script/)
- [Authentication is not yet supported](https://github.com/deniskrumko/ksqldb-ui/issues/6)

# How to use ksqlDB UI

**Note:** For production purposes use fixed version from [available tags](https://hub.docker.com/r/deniskrumko/ksqldb-ui/tags) instead of `deniskrumko/ksqldb-ui:latest`

## Using docker

```bash
# Download image
docker pull deniskrumko/ksqldb-ui:latest

# Run container
# You need to have config/production.toml file in current directory
docker run \
    -p 8080:8080 \
    -v $(PWD)/config:/config \
    --env APP_CONFIG=/config/production.toml \
    deniskrumko/ksqldb-ui:latest
```

## Using docker-compose.yml

1. Write `docker-compose.yml` file:

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

2. Run `docker-compose up -d`

3. Open browser and navigate to http://localhost:8080

Checkout working example of `ksqlDB` + `ksqlDB-UI` below.

## Using kubernetes manifests

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

Other manifests (like `ingress.yml` and so on) you can do on your own 👌

# Configuration

## Using `.toml` file and `APP_CONFIG` env var

Take a look at example config file – [config/example.toml](./config/example.toml)

To run ksqlDB UI you need to create own config file and add it using `APP_CONFIG` env var. See "How to use" section above.

Simplest configuration possible:

```toml
[servers.localhost]
url = "http://localhost:8090"
```

**Parameters description**

| Parameter                     | Description                                                                                                                          | Default | Required |
|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------|----------|
| `global.language`             | UI language. Supported languages: English (en), Russian (ru)                                                                         | "en"    | ❌        |
| `global.show_hint`            | Show hints on different pages                                                                                                        | true    | ❌        |
| `http.timeout`                | Timeout in seconds for ksqldb requests                                                                                               | 5       | ❌        |
| `history.enabled`             | Enable request history. Every user will see common history                                                                           | true    | ❌        |
| `history.size`                | how many requests will be saved to history (works as queue)                                                                          | 50      | ❌        |
| `server.CODE.url`             | URL to ksqldb server API                                                                                                             |         | ✅        |
| `server.CODE.name`            | custom name of environment (if empty - use server code)                                                                              |         | ❌        |
| `server.CODE.default`         | Use server as default then loading UI                                                                                                |         | ❌        |
| `server.CODE.topic_link`      | link to redirect to Kafka UI to see topic messages. Topic name is passed to `{}` placeholder in the URL                              |         | ❌        |
| `server.CODE.warning_message` | This message will be displayed as warning on every page in UI                                                                        |         | ❌        |
| `server.CODE.filters`         | Filter groups for stream/query list pages. Allows to quick search keyword in stream/query name. Must be a list of lists with strings |         | ❌        |

## Using only environment variables

KsqlDB UI settings works using [Dynaconf](https://www.dynaconf.com/) and that means that **all settings** can be described/overriden using env vars by following rules:

- Add `KSQLDB_UI__` prefix to each var
- Nested params separated using double underscores: `__`
- Use uppercase for env vars

For example, this `config.toml`:

```toml
[http]
timeout = 60

[servers.localhost]
url = 'http://localhost:8080'

[servers.production]
url = 'http://production:8080'
filters = [['Alice', 'Bob'], ['Red', 'Green', 'Yellow']]
```

... can be replaces using these env vars:

```bash
KSQLDB_UI__HTTP__TIMEOUT=60
KSQLDB_UI__SERVERS__LOCALHOST__URL=http://localhost:8080
KSQLDB_UI__SERVERS__PRODUCTION__URL=http://production:8080
KSQLDB_UI__SERVERS__PRODUCTION__FILTERS="[['Alice', 'Bob'], ['Red', 'Green', 'Yellow']]"
```

Notes:

- `APP_CONFIG` env var is not needed when using `KSQLDB_UI__` env vars, but you can use both
- `KSQLDB_UI__` env vars will **always override** configuration from `APP_CONFIG` file
- All available env vars can also be seen on `/debug` page after opening your ksqlDB UI

# Working example

In [docker-compose.yml](./docker-compose.yml) there are three components to work with:
- ksqldb
- ksqldb-ui
- Redpanda (this is just like Apache Kafka but better 😎)
- Redpanda UI

To run this example:

1. Download [docker-compose.yml](./docker-compose.yml) locally

2. Run command:

```bash
docker-compose up -d
```

3. Open ksqldb-ui in browser: http://localhost:8080 to create streams/queries

4. Open Redpanda UI in browser: http://localhost:8090 to create topics

# API

## POST `/api/process_file`

Upload file with SQL statements and get response.

Request with `request.sql` file:

```bash
curl -F "file=@./request.sql" http://localhost:8080/api/process_file?s=dev
```

File content:

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

- Powered by Python 3.12, FastAPI and Jinja2
- UI using [Bootstrap 5.3](https://getbootstrap.com/docs/5.3/)
- SQL editor using [Ace](https://ace.c9.io/)
- Icons from [Google fonts](https://fonts.google.com/icons?icon.size=24&icon.color=%23e3e3e3)
- Markdown tables from [tablesgenerator.com](https://www.tablesgenerator.com/markdown_tables)
