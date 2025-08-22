function buildTopology(query) {
  var g = new dagreD3.graphlib.Graph()
    .setGraph({"rankDir": "LR"})
    .setDefaultEdgeLabel(function () {
      return {};
    });

  const topologyNodes = Array.from(document.querySelectorAll(".topology"));
  let streams = [];
  let streamTopics = {};
  let queries = [];
  let queryState = {};
  let edges = [];

  // Find highlighted
  let params = new URLSearchParams(window.location.search);
  let highlighted = params.get("highlight");
  console.log("Highlighted:", highlighted);

  topologyNodes.forEach((node) => {
    let name = node.dataset.name;
    if (node.classList.contains("stream")) {
      streams.push(name);
      streamTopics[name] = node.dataset.topic;
    } else if (node.classList.contains("query")) {
      queries.push(name);
      queryState[name] = node.dataset.state;
      edges.push([node.dataset.source, name]);
      edges.push([name, node.dataset.sink]);
    }
  });

  // Add streams
  if (streams.length > 0) {
    streams.forEach(function (streamId) {
      g.setNode(streamId, {
        labelType: "html",
        label: `
        <a href="/streams/${streamId}?${query}" class="topology-node">
          <h2>${streamId}</h2>
          <p>topic: ${streamTopics[streamId]}</p>
        </a>`,
        class: highlighted === streamId ? "type-HL" : "type-STREAM",
      });
    });
  }

  // Add queries
  if (queries.length > 0) {
    queries.forEach(function (queryId) {
      g.setNode(queryId, {
        labelType: "html",
        label: `
        <a href="/queries/${queryId}?${query}" class="topology-node">
          <h2>${queryId}</h2>
          <p>query state: ${queryState[queryId]}</p>
        </a>`,
        class:  highlighted === queryId ? "type-HL" : `type-QUERY-${queryState[queryId]}`,
      });
    });
  }

  // Add edges
  if (edges.length > 0) {
    edges.forEach(function (edge) {
      g.setEdge(edge[0], edge[1]);
    });
  }

  g.nodes().forEach(function (v) {
    var node = g.node(v);
    node.rx = node.ry = 12;
  });

  return g;
}

function buildTopicsTopology(query) {
  var g = new dagreD3.graphlib.Graph()
    .setGraph({"rankDir": "LR"})
    .setDefaultEdgeLabel(function () {
      return {};
    });

  const topologyNodes = Array.from(document.querySelectorAll(".topology"));
  let streams = [];
  let streamTopics = {};
  let topics = new Set();
  let topicStreams = {};
  let queries = [];
  let queryState = {};
  let edges = [];

  // Find highlighted
  let params = new URLSearchParams(window.location.search);
  let highlighted = params.get("highlight");
  console.log("Highlighted:", highlighted);

  // Collect data from topology nodes
  topologyNodes.forEach((node) => {
    let name = node.dataset.name;
    if (node.classList.contains("stream")) {
      streams.push(name);
      let topicName = node.dataset.topic;
      streamTopics[name] = topicName;
      topics.add(topicName);

      // Group streams by topic
      if (!topicStreams[topicName]) {
        topicStreams[topicName] = [];
      }
      topicStreams[topicName].push(name);
    } else if (node.classList.contains("query")) {
      queries.push(name);
      queryState[name] = node.dataset.state;

      // Create edges between topics through streams
      let sourceTopic = streamTopics[node.dataset.source];
      let sinkTopic = streamTopics[node.dataset.sink];

      if (sourceTopic && sinkTopic && sourceTopic !== sinkTopic) {
        edges.push([sourceTopic, sinkTopic, name]); // Include query name for edge label
      }
    }
  });

  // Add topic nodes
  topics.forEach(function (topicId) {
    let streamsForTopic = topicStreams[topicId] || [];
    let streamsList = streamsForTopic.sort().map(stream =>
      `stream: ${stream}`
    ).join('<br>');

    g.setNode(topicId, {
      labelType: "html",
      label: `
      <a href="/topics/${topicId}?${query}" class="topology-node">
        <h2>${topicId}</h2>
        <p>${streamsList}</p>
      </a>`,
      class: highlighted === topicId ? "type-HL" : "type-TOPIC",
    });
  });

  // Add edges between topics
  if (edges.length > 0) {
    edges.forEach(function (edge) {
      g.setEdge(edge[0], edge[1]);
    });
  }

  g.nodes().forEach(function (v) {
    var node = g.node(v);
    node.rx = node.ry = 12;
  });

  return g;
}
