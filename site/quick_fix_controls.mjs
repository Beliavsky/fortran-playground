import {findQuickFix, applyQuickFix} from './fixes.mjs';

// Only the enhanced editor can guarantee a single native undo transaction.
export function createQuickFixControls({editor, button, note, config,
  onApplied = () => {}, detect = findQuickFix}) {
  let proposal = null, busy = false;
  function refresh() {
    const visible = Boolean(config.enableQuickFixes && proposal && editor.undoableClear);
    button.hidden = !visible;
    button.disabled = !visible || busy;
    button.title = visible ? proposal.description : '';
    note.hidden = !visible;
    note.textContent = visible ? `${proposal.description} Applying the fix does not compile or run; Ctrl+Z undoes it.` : '';
  }
  function clear() { proposal = null; refresh(); }
  button.onclick = () => {
    if (busy || !config.enableQuickFixes || !editor.undoableClear || !proposal) return;
    const fix = proposal;
    try {
      applyQuickFix(editor.getValue(), fix); // Validate the exact source snapshot.
    } catch { clear(); return; }
    clear();
    editor.applyEdit(fix.start, fix.end, fix.replacement);
    editor.focus();
    onApplied(fix);
  };
  clear();
  return {
    clear, refresh,
    setBusy(value) { busy = value; refresh(); },
    update(source, output, compiler, buildFailed) {
      proposal = config.enableQuickFixes && buildFailed ? detect(source, output, {
        enableQuickFixes: true, compiler, disabledRules: config.disabledQuickFixRules,
      }) : null;
      refresh();
    },
  };
}
