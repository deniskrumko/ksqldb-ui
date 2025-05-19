// Initializes the Ace editor for displaying the SQL statement.
function initAceEditor() {
  var editor = ace.edit("sql-statement");
  editor.setTheme("ace/theme/chrome");
  editor.session.setMode("ace/mode/sql");
  editor.session.setUseWrapMode(true);
  editor.setReadOnly(true);
}

// Builds and returns a dagreD3 graph object based on the topology nodes.
function buildGraph(query) {
  var g = new dagreD3.graphlib.Graph()
    .setGraph({})
    .setDefaultEdgeLabel(function () {
      return {};
    });

  const topologyNodes = Array.from(document.querySelectorAll(".topology"));

  let currentNode = null;
  let sources = [];
  let sinks = [];
  let readQueries = [];
  let readQuerySinksMap = {};
  let writeQueries = [];

  topologyNodes.forEach((node) => {
    let name = node.dataset.name;
    if (node.classList.contains("current")) {
      currentNode = name;
    } else if (node.classList.contains("source")) {
      sources.push(name);
    } else if (node.classList.contains("sink")) {
      sinks.push(name);
    } else if (node.classList.contains("read-query")) {
      readQueries.push(name);
      readQuerySinksMap[name] = Array.from(
        node.querySelectorAll(".read-query-sink")
      ).map((sink) => sink.dataset.name);
    } else if (node.classList.contains("write-query")) {
      writeQueries.push(name);
    }
  });

  if (currentNode) {
    g.setNode(currentNode, {
      labelType: "html",
      label: `<b class="accent-text">${currentNode}</b>`,
      class: "type-CURNODE",
    });
    console.log("Current node:", currentNode);
  } else {
    console.error("No current node found");
  }

  // Add read query nodes and edges
  if (readQueries.length > 0) {
    readQueries.forEach(function (queryId) {
      g.setNode(queryId, {
        labelType: "html",
        label: `<a href="/queries/${queryId}?${query}">${queryId}</a>`,
        class: "type-QUERY",
      });
      g.setEdge(currentNode, queryId);

      readQuerySinksMap[queryId].forEach(function (sink) {
        g.setEdge(queryId, sink);
        g.setNode(sink, {
          labelType: "html",
          label: `<a href="/streams/${sink}?${query}">${sink}</a>`,
          class: "type-SINK",
        });
      });
    });
  }

  // Add write query nodes and edges
  if (writeQueries.length > 0) {
    writeQueries.forEach(function (queryId) {
      g.setNode(queryId, {
        labelType: "html",
        label: `<a href="/queries/${queryId}?${query}">${queryId}</a>`,
        class: "type-QUERY",
      });
      g.setEdge(queryId, currentNode);
    });
  }

  if (sources.length > 0) {
    sources.forEach(function (streamId) {
      g.setNode(streamId, {
        labelType: "html",
        label: `<a href="/streams/${streamId}?${query}">${streamId}</a>`,
        class: "type-SINK",
      });
      g.setEdge(streamId, currentNode);
    });
  }

  if (sinks.length > 0) {
    sinks.forEach(function (streamId) {
      g.setNode(streamId, {
        labelType: "html",
        label: `<a href="/streams/${streamId}?${query}">${streamId}</a>`,
        class: "type-SINK",
      });
      g.setEdge(currentNode, streamId);
    });
  }

  g.nodes().forEach(function (v) {
    var node = g.node(v);
    node.rx = node.ry = 12;
  });

  return g;
}

// Renders the dagreD3 graph inside the SVG element.
function renderGraph(g, svgObj) {
  // Clear previous content
  while (svgObj.firstChild) {
    svgObj.removeChild(svgObj.firstChild);
  }

  var svg = d3.select(svgObj),
    svgGroup = svg.append("g");

  var render = new dagreD3.render();
  render(svgGroup, g);

  // Make node labels clickable
  d3.selectAll("g.node a").style("pointer-events", "all");

  // Center the graph
  var width = parseInt(svgObj.getAttribute("width"), 10) || 960;
  var xCenterOffset = (width - g.graph().width) / 2;
  svgGroup.attr("transform", "translate(" + xCenterOffset + ", 20)");
  svgObj.setAttribute("height", g.graph().height + 40);
}

// Initializes the SVG canvas for the topology graph.
function initSvgCanvas() {
  const svgParent = document.getElementById("svg-parent");
  const pageWidth = svgParent.offsetWidth || document.body.offsetWidth || 960;
  let svgObj = document.getElementById("svg-canvas");
  if (!svgObj) {
    svgObj = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgObj.setAttribute("id", "svg-canvas");
    svgParent.appendChild(svgObj);
  }
  svgObj.setAttribute("width", pageWidth);
  svgObj.setAttribute("height", "10");
  return svgObj;
}

// Handles window resize event to update the SVG graph width and re-render.
function handleResize(g) {
  const svgParent = document.getElementById("svg-parent");
  const svgObj = document.getElementById("svg-canvas");
  if (svgParent && svgObj && g) {
    const newWidth = svgParent.offsetWidth || document.body.offsetWidth || 960;
    svgObj.setAttribute("width", newWidth);
    renderGraph(g, svgObj);
  }
}
