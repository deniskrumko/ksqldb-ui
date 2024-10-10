![ksqldb-ui](https://github.com/deniskrumko/ksqldb-ui/blob/master/src/static/images/full_logo_readme.png?raw=true)

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/deniskrumko/ksqldb-ui/build-and-push.yml)](https://github.com/deniskrumko/visual-coordinates-tool/actions)
[![GitHub Release](https://img.shields.io/github/v/release/deniskrumko/ksqldb-ui)](https://github.com/deniskrumko/ksqldb-ui/releases)
[![Docker pulls](https://img.shields.io/docker/pulls/deniskrumko/ksqldb-ui)](https://hub.docker.com/r/deniskrumko/ksqldb-ui/tags)

Web UI for [ksqlDB](https://ksqldb.io/). Make requests and interact with queries or streams using browser instead of CLI. Written on Python, FastAPI and Jinja2.

Checkout image on Docker Hub: https://hub.docker.com/r/deniskrumko/ksqldb-ui

![preview](https://github.com/deniskrumko/ksqldb-ui/blob/master/src/static/images/preview.png?raw=true)

# Features

- Write SQL requests to manipulate streams/queries
- View list of existing queries/streams and detailed info
- Delete existing queries/streams
- See own history of requests (can be disabled in `config.toml`)

[Authentication is not yet supported](https://github.com/deniskrumko/ksqldb-ui/issues/6)

# How it works

KsqlDB UI works only using [REST API](https://docs.ksqldb.io/en/latest/developer-guide/api/) provided by ksqlDB itself and can't do more than it provides.

For example, you can't use `RUN SCRIPT` statement in this UI because [it can only be executed using file](https://docs.ksqldb.io/en/latest/developer-guide/ksqldb-reference/run-script/).

All statements that exist in ksqlDB [are listed in their documentation](https://docs.ksqldb.io/en/latest/developer-guide/ksqldb-reference/quick-reference/).

# How to use

For production purposes it is strongly recommended to use fixed version from [available tags](https://hub.docker.com/r/deniskrumko/ksqldb-ui/tags) instead of `deniskrumko/ksqldb-ui:latest`.

## Docker compose

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

## Kubernetes manifests

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
    [servers]

    [servers.development]
    url = 'http://your-development-ksqldb.com'
    topic_link = 'http://your-development-kafka-ui.com/topics/{}'

    [servers.production]
    url = 'http://your-production-ksqldb.com'
    topic_link = 'http://your-production-kafka-ui.com/topics/{}'
```

Other manifests (like `ingress.yml` and so on) you can do on your own :)

# Config example

Configuration supports multiple servers that can be selected in the UI.

```toml
[servers]

[servers.localhost]
url = 'http://0.0.0.0:8088'
topic_link = 'http://localhost:8090/topics/{}'

[servers.development]
url = 'http://your-development-ksqldb.com'
topic_link = 'http://your-development-kafka-ui.com/topics/{}'

[servers.production]
url = 'http://your-production-ksqldb.com'
topic_link = 'http://your-production-kafka-ui.com/topics/{}'
warning_message = 'This is a production environment. Please do not modify existing streams/queries.'

[history]
enabled = true
size = 50
```

Some explanation:

- `topic_link` is used to redirect to Apache Kafka or Redpanda UI to see topic messages. Topic name is passed to `{}` placeholder in the URL.
- `warning_message` is shown in the UI if you are in production. Totally optional.
- `history` is enabled by default. If you want to disable it, set `history.enabled = false` in your config.
