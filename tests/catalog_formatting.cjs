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
