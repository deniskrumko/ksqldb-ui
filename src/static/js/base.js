// Copies the SQL statement from the Ace editor to the clipboard
function copyEditor(editorId) {
  var editor = ace.edit(editorId);
  const text = editor.getValue();

  if (navigator.clipboard) {
    navigator.clipboard.writeText(text);
  } else {
    // fallback for older browsers
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }

  console.log("SQL statement copied to clipboard");
}

function setWrapText(editorId, wrapText) {
  var editor = ace.edit(editorId);
  editor.session.setUseWrapMode(wrapText);

  var btn = document.getElementById("wrap-text");
  if (wrapText) {
    btn.classList.add("active");
  } else {
    btn.classList.remove("active");
  }

  console.log("Wrap mode updated: ", wrapText);
  localStorage.setItem("wrap-text", wrapText);
  return wrapText;
}

function getWrapText() {
  const wrapText = localStorage.getItem("wrap-text");
  if (!wrapText) {
    console.log("Wrap text initialized");
    return true;
  } else {
    return wrapText === "true";
  }
}

function toggleWrapText(editorId) {
  const wrapText = getWrapText();
  setWrapText(editorId, !wrapText);
}

function loadWrapText(editorId) {
  setWrapText(editorId, getWrapText());
}

function pasteRespValue(e, isWrap=false) {
  let element = $(e);
  if (!isWrap) {
    element = element.parent().parent().next(".value").find("pre");
  }

  const text = element.text();
  editor.setValue(text);
  console.log('Pasted resp value of length', text.length);
}

function copyRespValue(e) {
  const text = $(e).parent().parent().next(".value").find("pre").text();
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text);
  } else {
    // fallback for older browsers
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }

  console.log('Copied resp value of length', text.length);
}

function togglePageHelp() {
  const helpSection = document.getElementById("page-help-section");
  if (helpSection) {
    helpSection.style.display = helpSection.style.display === "block" ? "none" : "block";
  }
}
