import {indentationSettings, indentationForLine} from './indentation.mjs';

export function countLines(text) {
  if (!text) return 0;
  const normalized = text.replace(/\r\n?/g, '\n');
  return normalized.split('\n').length - (normalized.endsWith('\n') ? 1 : 0);
}

// Keep a working textarea until the optional editor finishes loading.
export function createEditor(textarea, counter, onChange = () => {}) {
  let cm = null;
  let indentation = indentationSettings();
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
  function closingIndent(value, offset, allowBare = false) {
    const lines = value.slice(0, offset).split('\n');
    if (!/^\s*(?:end|else|case|class|type\s+is|rank|contains)/i.test(lines.at(-1))) return null;
    return indentationForLine(lines, lines.length - 1, indentation.width, allowBare).current;
  }
  function plainReplace(start, end, text, cursor = start + text.length) {
    textarea.setRangeText(text, start, end, 'end');
    textarea.setSelectionRange(cursor, cursor);
    changed();
  }
  textarea.addEventListener('input', event => {
    if (!cm && indentation.automatic && event?.inputType === 'insertText' && !event.isComposing) {
      const offset = textarea.selectionStart, start = textarea.value.lastIndexOf('\n', offset - 1) + 1;
      const desired = closingIndent(textarea.value, offset);
      if (desired !== null) {
        const old = /^\s*/.exec(textarea.value.slice(start, offset))[0].length;
        textarea.setRangeText(' '.repeat(desired), start, start + old, 'preserve');
      }
    }
    changed();
  });
  textarea.addEventListener('keydown', event => {
    if (cm || textarea.readOnly || event.isComposing || event.ctrlKey || event.metaKey || event.altKey) return;
    if (event.key === 'Escape') {textarea.blur?.(); return;}
    const start = textarea.selectionStart, end = textarea.selectionEnd;
    if (event.key === 'Enter' && indentation.automatic && start === end) {
      event.preventDefault();
      const lines = textarea.value.slice(0, start).split('\n');
      const hint = indentationForLine(lines, lines.length - 1, indentation.width);
      const lineStart = start - lines.at(-1).length, old = /^\s*/.exec(lines.at(-1))[0].length;
      const prefix = hint.current === null ? lines.at(-1) : ' '.repeat(hint.current) + lines.at(-1).slice(old);
      plainReplace(lineStart, end, prefix + '\n' + ' '.repeat(hint.next));
    } else if (event.key === 'Tab') {
      event.preventDefault();
      const first = textarea.value.lastIndexOf('\n', start - 1) + 1;
      if (!event.shiftKey && start === end) {
        plainReplace(start, end, ' '.repeat(indentation.width - (start - first) % indentation.width));
      } else {
        const last = textarea.value.indexOf('\n', end > start && textarea.value[end - 1] === '\n' ? end - 1 : end);
        const stop = last < 0 ? textarea.value.length : last;
        const text = textarea.value.slice(first, stop).split('\n').map(line => event.shiftKey ? line.replace(new RegExp(`^ {1,${indentation.width}}`), '') : ' '.repeat(indentation.width) + line).join('\n');
        textarea.setRangeText(text, first, stop, 'select');
        if (start === end) {
          const cursor = Math.max(first, start - (stop - first - text.length));
          textarea.setSelectionRange(cursor, cursor);
        }
        changed();
      }
    }
  });
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
    applyEdit(start, end, replacement) {
      if (!cm) throw new Error('Undoable edits require the enhanced editor.');
      cm.getDoc().changeGeneration(true);
      cm.replaceRange(replacement, cm.posFromIndex(start), cm.posFromIndex(end), '+quickfix');
      cm.getDoc().changeGeneration(true);
    },
    setReadOnly(value) {
      textarea.readOnly = value;
      cm?.setOption('readOnly', value);
    },
    focus() { if (cm) cm.focus(); else textarea.focus(); },
    refresh() { cm?.refresh(); },
    setIndentation(value) {
      indentation = indentationSettings(value);
      cm?.setOption('indentUnit', indentation.width);
      cm?.setOption('tabSize', indentation.width);
    },
    get undoableClear() { return cm !== null; },
    enhance(CodeMirror, mode, label) {
      cm = CodeMirror.fromTextArea(textarea, {
        mode, lineNumbers: true, gutters: ['CodeMirror-linenumbers', 'p2f-errors'], indentUnit: indentation.width, tabSize: indentation.width,
        indentWithTabs: false, readOnly: textarea.readOnly,
        viewportMargin: 10,
        extraKeys: {
          Enter(editor) {
            if (editor.getOption('readOnly')) return CodeMirror.Pass;
            if (!indentation.automatic) {editor.replaceSelection('\n', 'end', '+input'); return;}
            if (editor.somethingSelected() || editor.listSelections().length !== 1) return CodeMirror.Pass;
            const cursor = editor.getCursor(), lines = editor.getValue().slice(0, editor.indexFromPos(cursor)).split('\n');
            const hint = indentationForLine(lines, lines.length - 1, indentation.width);
            editor.operation(() => {
              if (hint.current !== null) {
                const old = /^\s*/.exec(lines.at(-1))[0].length;
                editor.replaceRange(' '.repeat(hint.current), {line: cursor.line, ch: 0}, {line: cursor.line, ch: old}, '+input');
              }
              editor.replaceSelection('\n' + ' '.repeat(hint.next), 'end', '+input');
            });
          },
          Tab(editor) {
            if (editor.getOption('readOnly')) return CodeMirror.Pass;
            if (editor.somethingSelected()) editor.indentSelection('add');
            else editor.replaceSelection(' '.repeat(indentation.width - editor.getCursor().ch % indentation.width), 'end', '+input');
          },
          'Shift-Tab': 'indentLess',
          Esc(editor) { editor.getInputField().blur(); },
        },
      });
      cm.getInputField().setAttribute('aria-label', label);
      textarea.labels?.[0]?.addEventListener('click', event => { event.preventDefault(); cm.focus(); });
      cm.on('change', changed);
      cm.on('inputRead', (editor, change) => {
        if (!indentation.automatic || editor.getOption('readOnly') || change.origin !== '+input' || change.text.length !== 1 || editor.listSelections().length !== 1) return;
        const cursor = editor.getCursor(), desired = closingIndent(editor.getValue(), editor.indexFromPos(cursor));
        if (desired === null) return;
        const old = /^\s*/.exec(editor.getLine(cursor.line))[0].length;
        if (old !== desired) editor.replaceRange(' '.repeat(desired), {line: cursor.line, ch: 0}, {line: cursor.line, ch: old}, '+input');
      });
      renderDiagnostics();
    },
  };
  const n = countLines(textarea.value);
  counter.textContent = `${n} ${n === 1 ? 'line' : 'lines'}`;
  return api;
}
