export function countLines(text) {
  if (!text) return 0;
  const normalized = text.replace(/\r\n?/g, '\n');
  return normalized.split('\n').length - (normalized.endsWith('\n') ? 1 : 0);
}

// Keep a working textarea until the optional editor finishes loading.
export function createEditor(textarea, counter, onChange = () => {}) {
  let cm = null;
  let diagnostics = [], errorLines = [], errorMarks = [];
  function clearMarkers() {
    for (const handle of errorLines) {
      cm.removeLineClass(handle, 'background', 'p2f-error-line');
      cm.setGutterMarker(handle, 'p2f-errors', null);
    }
    for (const mark of errorMarks) mark.clear();
    errorLines = []; errorMarks = [];
  }
  function renderDiagnostics() {
    if (!cm) return;
    clearMarkers();
    const grouped = new Map();
    for (const item of diagnostics) {
      const index = item.line - 1;
      if (!grouped.has(index)) grouped.set(index, []);
      grouped.get(index).push(item);
    }
    for (const [index, items] of grouped) {
      const message = items.map(item => item.message).join('\n');
      const handle = cm.addLineClass(index, 'background', 'p2f-error-line');
      errorLines.push(handle);
      const marker = document.createElement('button');
      marker.type = 'button'; marker.className = 'p2f-error-marker';
      marker.textContent = '!'; marker.title = message;
      marker.setAttribute('aria-label', `Line ${index + 1}: ${message}`);
      marker.onclick = () => api.goToDiagnostic(items[0]);
      cm.setGutterMarker(handle, 'p2f-errors', marker);
      const length = cm.getLine(index).length;
      if (length) errorMarks.push(cm.markText({line: index, ch: 0}, {line: index, ch: length}, {title: message}));
      for (const item of items) {
        if (item.column && length) {
          const ch = Math.min(length - 1, item.column - 1);
          errorMarks.push(cm.markText({line: index, ch}, {line: index, ch: ch + 1}, {className: 'p2f-error-column', title: item.message}));
        }
      }
    }
    if (diagnostics.length) cm.scrollIntoView({line: diagnostics[0].line - 1, ch: 0}, 60);
  }
  function changed() {
    api.clearDiagnostics();
    if (cm) textarea.value = cm.getValue();
    const count = countLines(textarea.value);
    counter.textContent = `${count} ${count === 1 ? 'line' : 'lines'}`;
    onChange();
  }
  textarea.addEventListener('input', changed);
  const api = {
    getValue: () => cm ? cm.getValue() : textarea.value,
    clearDiagnostics() { clearMarkers(); diagnostics = []; },
    setDiagnostics(items) {
      api.clearDiagnostics();
      const lines = api.getValue().replace(/\r\n?/g, '\n').split('\n');
      diagnostics = items.filter(item => Number.isInteger(item.line) && item.line > 0 && item.line <= lines.length);
      renderDiagnostics();
    },
    goToDiagnostic(item = diagnostics[0]) {
      if (!item) return;
      const line = item.line - 1;
      const lines = api.getValue().replace(/\r\n?/g, '\n').split('\n');
      const ch = Math.max(0, Math.min(lines[line].length, (item.column || 1) - 1));
      if (cm) {
        cm.setCursor({line, ch}); cm.scrollIntoView({line, ch}, 60); cm.focus();
      } else {
        const offset = textarea.value.split('\n').slice(0, line).reduce((total, text) => total + text.length + 1, 0);
        textarea.focus(); textarea.setSelectionRange(offset, offset + lines[line].length);
      }
    },
    setValue(value, undoable = false) {
      if (cm && undoable) {
        cm.getDoc().changeGeneration(true);
        cm.replaceRange(value, { line: 0, ch: 0 }, cm.posFromIndex(cm.getValue().length), '+clear');
        cm.getDoc().changeGeneration(true);
      } else if (cm) {
        cm.setValue(value);
      } else {
        textarea.value = value;
        changed();
      }
    },
    setReadOnly(value) {
      textarea.readOnly = value;
      cm?.setOption('readOnly', value);
    },
    focus() { if (cm) cm.focus(); else textarea.focus(); },
    refresh() { cm?.refresh(); },
    get undoableClear() { return cm !== null; },
    enhance(CodeMirror, mode, label) {
      cm = CodeMirror.fromTextArea(textarea, {
        mode, lineNumbers: true, gutters: ['CodeMirror-linenumbers', 'p2f-errors'], indentUnit: 4, tabSize: 4,
        indentWithTabs: false, readOnly: textarea.readOnly,
        viewportMargin: 10,
        extraKeys: {
          Tab(editor) {
            if (editor.getOption('readOnly')) return CodeMirror.Pass;
            if (editor.somethingSelected()) editor.indentSelection('add');
            else editor.replaceSelection(' '.repeat(4 - editor.getCursor().ch % 4), 'end', '+input');
          },
          'Shift-Tab': 'indentLess',
          Esc(editor) { editor.getInputField().blur(); },
        },
      });
      cm.getInputField().setAttribute('aria-label', label);
      textarea.labels?.[0]?.addEventListener('click', event => { event.preventDefault(); cm.focus(); });
      cm.on('change', changed);
      renderDiagnostics();
    },
  };
  const n = countLines(textarea.value);
  counter.textContent = `${n} ${n === 1 ? 'line' : 'lines'}`;
  return api;
}
