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
  let allReferencedStreams = new Set();

  // Find highlighted
  let params = new URLSearchParams(window.location.search);
  let highlighted = params.get("highlight");
  console.log("Highlighted:", highlighted);

  // First pass: collect all streams and their topics
  topologyNodes.forEach((node) => {
    let name = node.dataset.name;
    if (node.classList.contains("stream")) {
      streams.push(name);
      let topicName = node.dataset.topic;
      streamTopics[name] = topicName;
      topics.add(topicName);
      allReferencedStreams.add(name);

      // Group streams by topic
      if (!topicStreams[topicName]) {
        topicStreams[topicName] = [];
      }
      topicStreams[topicName].push(name);
      console.log(`Found stream: ${name} -> topic: ${topicName}`);
    } else if (node.classList.contains("query")) {
      // Collect all referenced streams from queries
      if (node.dataset.source) {
        allReferencedStreams.add(node.dataset.source);
      }
      if (node.dataset.sink) {
        allReferencedStreams.add(node.dataset.sink);
      }
    }
  });

  console.log("All streams:", Object.keys(streamTopics));
  console.log("All referenced streams:", Array.from(allReferencedStreams));
  console.log("All topics:", Array.from(topics));

  // Check for missing stream definitions and handle them
  allReferencedStreams.forEach(streamName => {
    if (!streamTopics[streamName]) {
      console.warn(`Stream '${streamName}' is referenced in queries but has no topic definition`);
      // For missing streams (usually sinks), assume the topic name is the same as the stream name
      // This is a common convention in ksqlDB
      let assumedTopic = streamName.toLowerCase();
      streamTopics[streamName] = assumedTopic;
      topics.add(assumedTopic);

      if (!topicStreams[assumedTopic]) {
        topicStreams[assumedTopic] = [];
      }
      topicStreams[assumedTopic].push(streamName);
      console.log(`Assumed topic for stream '${streamName}': ${assumedTopic}`);
    }
  });

  // Second pass: collect queries and create edges between topics
  let edges = new Set(); // Use Set to avoid duplicate edges
  topologyNodes.forEach((node) => {
    let name = node.dataset.name;
    if (node.classList.contains("query")) {
      queries.push(name);
      queryState[name] = node.dataset.state;

      // Create edges between topics through streams
      let sourceStream = node.dataset.source;
      let sinkStream = node.dataset.sink;
      let sourceTopic = streamTopics[sourceStream];
      let sinkTopic = streamTopics[sinkStream];

      // Debug logging to help identify missing relations
      if (!sourceTopic) {
        console.warn(`Missing source topic for stream: ${sourceStream}, query: ${name}`);
      }
      if (!sinkTopic) {
        console.warn(`Missing sink topic for stream: ${sinkStream}, query: ${name}`);
      }

      if (sourceTopic && sinkTopic && sourceTopic !== sinkTopic) {
        // Create a unique edge identifier to avoid duplicates
        let edgeKey = `${sourceTopic}->${sinkTopic}`;
        edges.add(edgeKey);
        console.log(`Added edge: ${sourceTopic} -> ${sinkTopic} (via query ${name})`);
      } else if (sourceTopic && sinkTopic && sourceTopic === sinkTopic) {
        console.log(`Skipped self-loop: ${sourceTopic} (via query ${name})`);
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
  edges.forEach(function (edgeKey) {
    let [sourceTopic, sinkTopic] = edgeKey.split('->');
    g.setEdge(sourceTopic, sinkTopic);
  });

  g.nodes().forEach(function (v) {
    var node = g.node(v);
    node.rx = node.ry = 12;
  });

  return g;
}
