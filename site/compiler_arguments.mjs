// The service advertises choices as token lists grouped by conflicting settings.
export function compilerArguments(spec, selection, additional = []) {
  if (!Array.isArray(additional) || additional.length > 32 ||
      additional.some(arg => typeof arg !== 'string' || !arg || arg.length > 128)) {
    throw new Error('Additional options must contain at most 32 short arguments.');
  }
  const flags = [...(spec?.presets?.[selection.preset || 'default'] || []),
    ...(spec?.standards?.[selection.standard || 'default'] || [])];
  if (selection.images !== undefined) {
    const coarrayFlags = spec?.coarray_images?.[String(selection.images)];
    if (![1, 2, 4].includes(selection.images) || !coarrayFlags) {
      throw new Error('This compiler/service has not verified the requested coarray image count.');
    }
    flags.push(...coarrayFlags);
  }
  for (const key of ['warnings', 'fast_math', 'preprocess']) {
    if (selection[key]) flags.push(...(spec?.extras?.[key] || []));
  }
  if (!additional.length) return flags;
  const groups = spec?.additional_options || {};
  if (!Object.keys(groups).length) throw new Error('Additional options are unavailable for this compiler/service.');
  const choices = Object.entries(groups).flatMap(([group, values]) => values.map(choice => ({group, choice})));
  const seen = new Map();
  for (const [arguments_, strict] of [[flags, false], [additional, true]]) {
    for (let index = 0; index < arguments_.length;) {
      const match = choices.find(({choice}) => choice.every((arg, offset) => arguments_[index + offset] === arg));
      if (!match) {
        if (strict) throw new Error(`Unsupported additional option: ${arguments_[index]}. Choose an advertised option.`);
        index++; continue;
      }
      const {group, choice} = match;
      if (seen.has(group) && JSON.stringify(seen.get(group)) !== JSON.stringify(choice)) {
        throw new Error(`Conflicting ${group} options: ${seen.get(group).join(' ')} and ${choice.join(' ')}.`);
      }
      seen.set(group, choice);
      index += choice.length;
    }
  }
  return [...flags, ...additional];
}

export function optionTokens(text) {
  return text.trim() ? text.trim().split(/\s+/) : [];
}
