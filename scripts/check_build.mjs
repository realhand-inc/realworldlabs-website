// Deployment gate: verify the exact static artifacts validated by the Python builder.
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname, relative, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const manifestIndex = process.argv.indexOf('--manifest');
const manifestPath = manifestIndex >= 0 ? resolve(process.argv[manifestIndex + 1]) : resolve(root, 'content/build-state.json');
// Normalize UTF-8 text regardless of its extension; preserve binary asset bytes.
function digest(path) {
  let data = readFileSync(path);
  if (!data.includes(0)) {
    const decoded = data.toString('utf8');
    if (Buffer.from(decoded, 'utf8').equals(data)) {
      data = Buffer.from(decoded.replace(/\r\n/g, '\n'), 'utf8');
    }
  }
  return createHash('sha256').update(data).digest('hex');
}
if (!existsSync(manifestPath)) {
  console.error('Missing build state. Run npm run build and include the generated public files.');
  process.exit(1);
}
const state = JSON.parse(readFileSync(manifestPath, 'utf8'));
const errors = [];
if (state.version !== 1 || !state.inputs || !state.outputs) errors.push('Invalid build state.');
let files = 0;
for (const [kind, entries] of [['source', state.inputs || {}], ['output', state.outputs || {}]]) {
  for (const [name, expected] of Object.entries(entries)) {
    const path = resolve(root, name);
    const fromRoot = relative(root, path);
    if (isAbsolute(fromRoot) || fromRoot.startsWith('..')) {
      errors.push('Invalid build path: ' + name);
      continue;
    }
    files++;
    if (!existsSync(path)) errors.push('Missing ' + kind + ': ' + name);
    else if (digest(path) !== expected) errors.push('Changed ' + kind + ': ' + name);
  }
}
const blogCount = Object.keys(state.inputs || {}).filter(name => /^content\/blog-[^/]+\.json$/.test(name)).length;
const expectedPages = 12 + blogCount; // Shared pages, product pages, 404, and every article.
if (blogCount < 1 || Object.keys(state.outputs || {}).filter(name => name.endsWith('.html')).length !== expectedPages) errors.push('Expected ' + expectedPages + ' generated HTML pages.');
if (errors.length) {
  console.error(errors.join('\n') + '\nRun npm run build, review the result, and include the updated generated files.');
  process.exit(1);
}
console.log('Verified ' + files + ' source and generated files. Static deployment artifacts are current.');
