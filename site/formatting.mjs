// Apply only successful, current results, using the editor's single Undo step.
export function applyFormatting(editor, source, result) {
  if (editor.getValue() !== source) throw new Error('Source changed; formatting discarded.');
  if (!editor.undoableClear) throw new Error('Formatting requires the enhanced editor.');
  if (!result.ok || typeof result.formatted_source !== 'string' || !result.formatted_source.trim()
      || new TextEncoder().encode(result.formatted_source).length > 100000) {
    throw new Error(result.error || 'No valid formatted source returned.');
  }
  const changed = result.formatted_source !== source;
  if (changed) editor.setValue(result.formatted_source, true);
  return changed;
}
