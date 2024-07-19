# ksqldb-ui

Free and simple way to interact with [ksqlDB](https://ksqldb.io/) using UI.

# WORK IN PROGRESS! 🫡

CREATE STREAM IF NOT EXISTS source_stream (
  message STRING
) WITH (
  KAFKA_TOPIC = 'input-topic',
  VALUE_FORMAT = 'JSON'
);

resp 200 [{'@type': 'warning_entity', 'statementText': "CREATE STREAM IF NOT EXISTS source_stream ( message STRING) WITH ( KAFKA_TOPIC = 'input-topic', VALUE_FORMAT = 'JSON');", 'message': 'Cannot add stream `SOURCE_STREAM`: A stream with the same name already exists.', 'warnings': []}]
req b'{"ksql": "CREATE STREAM IF NOT EXISTS source_stream ( message STRING) WITH ( KAFKA_TOPIC = \'input-topic\', VALUE_FORMAT = \'JSON\');"}'

resp 200 [{'@type': 'currentStatus', 'statementText': "CREATE STREAM IF NOT EXISTS SOURCE_STREAM2 (MESSAGE STRING) WITH (CLEANUP_POLICY='delete', KAFKA_TOPIC='input-topic', KEY_FORMAT='KAFKA', VALUE_FORMAT='JSON');", 'commandId': 'stream/`SOURCE_STREAM2`/create', 'commandStatus': {'status': 'SUCCESS', 'message': 'Stream created', 'queryId': None}, 'commandSequenceNumber': 7, 'warnings': []}] req b'{"ksql": "CREATE STREAM IF NOT EXISTS source_stream2 ( message STRING) WITH ( KAFKA_TOPIC = \'input-topic\', VALUE_FORMAT = \'JSON\');"}'

resp 400 {'@type': 'statement_error', 'error_code': 40001, 'message': "line 1:13: Syntax Error\nmissing ';' at ''", 'statementText': 'SHOW STREAMS', 'entities': []} req b'{"ksql": "SHOW STREAMS"}'

resp 200 [{'@type': 'streams', 'statementText': 'SHOW STREAMS;', 'streams': [{'type': 'STREAM', 'name': 'KSQL_PROCESSING_LOG', 'topic': 'ksql-local-test-serverksql_processing_log', 'keyFormat': 'KAFKA', 'valueFormat': 'JSON', 'isWindowed': False}, {'type': 'STREAM', 'name': 'SOURCE_STREAM', 'topic': 'input-topic', 'keyFormat': 'KAFKA', 'valueFormat': 'JSON', 'isWindowed': False}, {'type': 'STREAM', 'name': 'SOURCE_STREAM2', 'topic': 'input-topic', 'keyFormat': 'KAFKA', 'valueFormat': 'JSON', 'isWindowed': False}], 'warnings': []}] req b'{"ksql": "SHOW STREAMS;"}'
