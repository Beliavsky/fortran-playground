// Only PNG data is displayed; returned HTML, SVG and scripts are never inserted.
export function renderPlots(parent, result) {
  if (!result?.plots?.length && !result?.plot_notes?.length) return;
  const section = document.createElement('section');
  const heading = document.createElement('h3'); heading.textContent = 'Plots'; section.appendChild(heading);
  let total = 0;
  for (const plot of (result.plots ?? []).slice(0, 4)) {
    if (plot.mime !== 'image/png' || typeof plot.data !== 'string' || !/^[A-Za-z0-9+/]*={0,2}$/.test(plot.data)) continue;
    total += plot.data.length;
    if (total > 1398112 || !plot.data.startsWith('iVBORw0KGgo')) continue;
    const figure = document.createElement('figure');
    const img = document.createElement('img'); img.src = 'data:image/png;base64,' + plot.data;
    img.alt = String(plot.name || 'Program plot'); img.style.maxWidth = '100%'; img.style.height = 'auto';
    const caption = document.createElement('figcaption'); caption.textContent = img.alt;
    const download = document.createElement('a'); download.href = img.src; download.download = 'plot.png';
    download.textContent = 'Download PNG';
    figure.appendChild(img); figure.appendChild(caption); figure.appendChild(download); section.appendChild(figure);
  }
  for (const note of result.plot_notes ?? []) {const p = document.createElement('p'); p.textContent = String(note); section.appendChild(p);}
  parent.appendChild(section);
}
