// Copies the SQL statement from the Ace editor to the clipboard
function copyAceEditorToClipboard(editorId) {
  var editor = ace.edit(editorId);
  const text = editor.getValue();

  if (navigator.clipboard) {
    navigator.clipboard.writeText(text);
  } else {
    // fallback for older browsers
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
  }

  console.log('SQL statement copied to clipboard');
}
