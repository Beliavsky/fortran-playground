import assert from 'node:assert/strict';
import {renderPlots} from '../site/plots.mjs';
import {renderPlots as localPlots} from '../local_site/plots.mjs';

class Element {
  constructor(tag) {this.tag = tag; this.children = []; this.style = {};}
  appendChild(child) {this.children.push(child);}
}
globalThis.document = {createElement: tag => new Element(tag)};
const data = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC';
for (const render of [renderPlots, localPlots]) {
  const parent = new Element('div');
  render(parent, {}); assert.equal(parent.children.length, 0);
  render(parent, {plots: [{mime: 'text/html', data: '<script>alert(1)</script>'},
    {mime: 'image/png', name: '<img onerror=alert(1)>', data}], plot_notes: ['Limit reached']});
  const section = parent.children[0];
  assert.equal(section.children[0].textContent, 'Plots');
  const figure = section.children[1];
  assert.equal(figure.children[0].src, 'data:image/png;base64,' + data);
  assert.equal(figure.children[0].style.maxWidth, '100%');
  assert.equal(figure.children[1].textContent, '<img onerror=alert(1)>');
  assert.equal(figure.children[2].download, 'plot.png');
  assert.equal(section.children[2].textContent, 'Limit reached');
}
console.log('Hosted/local PNG rendering, download links, labels and non-PNG rejection passed.');
