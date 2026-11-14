const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const context = {};
vm.runInNewContext(fs.readFileSync(process.argv[2] || 'assets/formatting.js', 'utf8'), context);
const {normalizeFortran, normalizeDeclaration, normalizeDescription, initializeFormatting} = context.FortranCatalogFormatting;
for (const [source, expected] of [
  ['REAL,INTENT(OUT)::X(:,:)', 'real, intent(out) :: x(:, :)'],
  ['REAL    ::    X', 'real :: x'],
  ['REAL X', 'real :: x'],
  ['DOUBLE PRECISION X', 'double precision :: x'],
  ['REAL*8 X', 'real*8 :: x'],
  ['CHARACTER(LEN=*) X', 'character(len=*) :: x'],
  ["CHARACTER X='::' ! Keep COMMENT", "character :: x='::' ! Keep COMMENT"],
  ["CHARACTER(LEN=4)::X='A::B'", "character(len=4) :: x='A::B'"],
  ['OPTIONAL X', 'optional :: x']
]) assert.equal(normalizeDeclaration(source), expected);
assert.equal(normalizeFortran('CALL Solve(A,B,   C)'), 'call solve(a, b, c)');
assert.equal(normalizeFortran('REAL(WP),ALLOCATABLE,INTENT(OUT) :: X(:,:)'), 'real(wp), allocatable, intent(out) :: x(:, :)');
assert.equal(normalizeFortran(`CALL F('Keep,UPPER','it''s,Exact', "A,""B") ! Keep,COMMENT`),
  `call f('Keep,UPPER', 'it''s,Exact', "A,""B") ! Keep,COMMENT`);
assert.equal(normalizeFortran('CALL F(A, &\n    B,\n C)\n! Upper,COMMENT\n#define FEATURE_NAME X'),
  'call f(a, &\n    b,\n c)\n! Upper,COMMENT\n#define FEATURE_NAME X');
const desc = 'Source dummy: X\n\nREAL :: X\nKeep This,COMMENT 😀\n\nOPTIONAL :: X';
const first = Array.from(desc.slice(0, desc.indexOf('REAL'))).length;
const last = Array.from(desc.slice(0, desc.indexOf('OPTIONAL'))).length;
assert.equal(normalizeDescription(desc, [[first,first+'REAL :: X'.length],[last,last+'OPTIONAL :: X'.length]]),
  'Source dummy: X\n\nreal :: x\nKeep This,COMMENT 😀\n\noptional :: x');

function fixture(stored, denied=false) {
  const control={checked:false, addEventListener(name,handler) {this[name]=handler;}};
  // A comma and its whitespace straddle annotation nodes; strings and comments
  // also cross nodes, so formatting each span separately would corrupt them.
  const nodes=["CALL F(", "[X]", ",", "  Y, 'Keep,UP", "PER') ! Exact, COMMENT 😀"].map(data=>({data}));
  const declarations=[{data:'REAL(WP), INTENT(OUT)::X(:,:), Y'}];
  declarations.classList={contains(name) {return name==='declaration-code';}};
  declarations.getAttribute=()=> 'REAL(WP), INTENT(OUT)::X(:,:)';
  const example={data:'CALL F(X,Y)'};
  const attrs={'data-intent-description':desc,'data-argument-label':'X',
    'data-code-ranges':JSON.stringify([[first,first+9],[last,last+13]])};
  const tooltip={getAttribute(name) {return attrs[name];},setAttribute(name,value) {attrs[name]=value;}};
  const doc={getElementById(id) {return id==='original-formatting'?control:null;},
    querySelectorAll(selector) {return selector==='.argument-intent'?[tooltip]:[nodes,declarations];},
    createTreeWalker(root) {let i=0;return {nextNode() {return root[i++] || null;}};}};
  const storage=new Map(stored ? [['fortran-catalog-original-formatting','true']] : []);
  const win={localStorage:{getItem(key) {if(denied)throw Error('blocked');return storage.get(key);},
    setItem(key,value) {if(denied)throw Error('blocked');storage.set(key,value);}}};
  const original=nodes.map(n=>n.data).join('');
  initializeFormatting(doc,win);
  return {control,nodes,declarations,example,attrs,storage,original};
}
for (const denied of [false,true]) {
  const f=fixture(false,denied);
  assert.equal(f.nodes.map(n=>n.data).join(''), "call f([x], y, 'Keep,UPPER') ! Exact, COMMENT 😀");
  assert.equal(f.declarations[0].data, 'real(wp), intent(out) :: x(:, :)');
  assert.equal(f.example.data,'CALL F(X,Y)');
  assert.match(f.attrs.title,/^x: Source dummy: X/);
  assert.ok(f.attrs.title.includes('real :: x'));
  assert.ok(f.attrs.title.includes('Keep This,COMMENT 😀'));
  assert.equal(f.attrs.title,f.attrs['aria-label']);
  f.control.checked=true;f.control.change();
  assert.equal(f.nodes.map(n=>n.data).join(''),f.original);
  assert.equal(f.declarations[0].data,'REAL(WP), INTENT(OUT)::X(:,:), Y');
  assert.equal(f.attrs.title,'X: '+desc);
  if (!denied) assert.equal(f.storage.get('fortran-catalog-original-formatting'),'true');
  f.control.checked=false;f.control.change();
  assert.ok(f.attrs.title.includes('optional :: x'));
}
const restored=fixture(true);
assert.equal(restored.nodes.map(n=>n.data).join(''),restored.original);
assert.equal(restored.control.checked,true);
console.log('Catalog formatting: default normalization, exact restoration, annotations, comments, Unicode, examples and storage passed.');


const {fortranTokens, highlightCode} = context.FortranCatalogFormatting;
function colored(source) {return Array.from(fortranTokens(source), t => [source.slice(t.start, t.end), t.kind]);}
assert.deepEqual(colored('REAL(wp), INTENT(OUT) :: x = -1.25e-3_wp ! CALL NotCode'), [
  ['REAL','type'], ['INTENT','keyword'], ['OUT','keyword'], ['1.25e-3_wp','number'], ['! CALL NotCode','comment']
]);
assert.deepEqual(colored(`CALL F('it''s ! REAL', Z'FF', .TRUE., 3_8)\n#define X 1`), [
  ['CALL','keyword'], ["'it''s ! REAL'",'string'], ["Z'FF'",'string'], ['.TRUE.','number'], ['3_8','number'], ['#define X 1','comment']
]);
assert.deepEqual(colored('call REAL_solver(real_data)'), [['call','keyword']]);

// Small DOM fixture exercising the actual tree-walking/replacement API. The
// original semantic links/annotation elements and text nodes must survive.
class DomNode {
  constructor(tag, data='') {this.tagName=tag; this.data=data; this.childNodes=[]; this.parentNode=null; this.attrs={};}
  appendChild(node) {this.childNodes.push(node);node.parentNode=this;return node;}
  replaceChild(node, old) {
    const i=this.childNodes.indexOf(old);assert.notEqual(i,-1);
    this.childNodes[i]=node;node.parentNode=this;old.parentNode=null;return old;
  }
  set textContent(text) {this.childNodes=[];this.appendChild(new DomNode('#text',text));}
  get textContent() {return this.tagName==='#text'?this.data:this.childNodes.map(n=>n.textContent).join('');}
  get className() {return this.attrs.class || '';}
  set className(text) {this.attrs.class=text;}
  get classList() {return {contains:name=>this.className.split(/\s+/).includes(name)};}
  getAttribute(name) {return this.attrs[name] ?? null;}
  setAttribute(name,value) {this.attrs[name]=value;}
}
function textNodes(root) {
  return root.childNodes.flatMap(n=>n.tagName==='#text'?[n]:textNodes(n));
}
function descendants(root) {return root.childNodes.flatMap(n=>[n,...descendants(n)]);}
const callRoot=new DomNode('code'), anchor=callRoot.appendChild(new DomNode('a'));
anchor.setAttribute('href','https://example.test/src.f90#L1');
const callPrefix=anchor.appendChild(new DomNode('#text','CA'));
anchor.appendChild(new DomNode('span')).textContent='LL solver%solve(';
const argument=anchor.appendChild(new DomNode('span'));
argument.className='argument-intent';argument.textContent='OUT';
argument.setAttribute('tabindex','0');argument.setAttribute('data-argument-label','OUT');
argument.setAttribute('data-intent-description','REAL, INTENT(OUT) :: OUT(:,:)');
argument.setAttribute('data-code-ranges',JSON.stringify([[0,'REAL, INTENT(OUT) :: OUT(:,:)'.length]]));
anchor.appendChild(new DomNode('#text',", 'Keep"));
anchor.appendChild(new DomNode('span')).textContent=",UPPER', 1.5e-2_wp)";
const declarationRoot=new DomNode('code'), declaration=declarationRoot.appendChild(new DomNode('span'));
declaration.className='declaration-code';declaration.textContent='REAL, ALLOCATABLE, INTENT(OUT)::OUT(:,:), OTHER';
declaration.setAttribute('data-normalized-code','REAL, ALLOCATABLE, INTENT(OUT)::OUT(:,:)');
declarationRoot.appendChild(new DomNode('#text',' ! Exact Comment <script>'));
const originalCall=callRoot.textContent, originalDeclaration=declarationRoot.textContent;
const toggle={checked:false,addEventListener(name,callback) {this[name]=callback;}};
const dom={getElementById:()=>toggle,
  querySelectorAll(selector) {
    if(selector==='.argument-intent')return [argument];
    return selector.includes('pre > code')?[callRoot,declarationRoot]:[callRoot,declaration];
  },
  createTreeWalker(root) {const nodes=textNodes(root);let i=0;return {nextNode:()=>nodes[i++] || null};},
  createElement:tag=>new DomNode(tag),createTextNode:text=>new DomNode('#text',text)};
const win={localStorage:{getItem:()=>null,setItem() {}}};
initializeFormatting(dom,win);
assert.equal(callRoot.textContent,"call solver%solve(out, 'Keep,UPPER', 1.5e-2_wp)");
assert.equal(declarationRoot.textContent,'real, allocatable, intent(out) :: out(:, :) ! Exact Comment <script>');
assert.ok(descendants(callRoot).some(n=>n.className==='syntax-keyword'));
assert.ok(descendants(callRoot).some(n=>n.className==='syntax-string'));
assert.ok(descendants(callRoot).some(n=>n.className==='syntax-number'));
assert.ok(descendants(declarationRoot).some(n=>n.className==='syntax-type'));
assert.ok(descendants(declarationRoot).some(n=>n.className==='syntax-comment'));
const syntaxCount=root=>descendants(root).filter(n=>n.className.startsWith('syntax-')).length;
const count=syntaxCount(callRoot)+syntaxCount(declarationRoot);
for(let i=0;i<4;i++) {
  toggle.checked=true;toggle.change();
  assert.equal(callRoot.textContent,originalCall);
  assert.equal(declarationRoot.textContent,originalDeclaration);
  assert.ok(syntaxCount(callRoot)>0); // Highlighting stays active in original mode.
  toggle.checked=false;toggle.change();
  assert.equal(syntaxCount(callRoot)+syntaxCount(declarationRoot),count);
  assert.equal(argument.parentNode,anchor);
  assert.equal(anchor.getAttribute('href'),'https://example.test/src.f90#L1');
  assert.equal(argument.getAttribute('tabindex'),'0');
  assert.equal(argument.getAttribute('title'),argument.getAttribute('aria-label'));
}
assert.ok(!descendants(declarationRoot).some(n=>n.tagName==='script'));
const standalone=new DomNode('code'), originalNode=standalone.appendChild(new DomNode('#text','CALL F()'));
const remove=highlightCode(dom,[standalone]);
assert.equal(standalone.textContent,'CALL F()');remove();
assert.equal(standalone.childNodes[0],originalNode);
assert.equal(callPrefix.data,'ca');
console.log('Fortran highlighting: tokens, split annotations, safe text, exact restoration, links and tooltips passed.');
