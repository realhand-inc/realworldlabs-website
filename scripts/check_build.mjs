// Deployment gate: verify the exact static artifacts validated by the Python builder.
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname, extname, relative, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const manifestIndex = process.argv.indexOf('--manifest');
const manifestPath = manifestIndex >= 0 ? resolve(process.argv[manifestIndex + 1]) : resolve(root, 'content/build-state.json');
const textExtensions = new Set(['.py','.json','.js','.mjs','.css','.html','.xml','.txt','.svg','.webmanifest']);
function digest(path) {
  let data = readFileSync(path);
  if (textExtensions.has(extname(path))) data = Buffer.from(data.toString('utf8').replace(/\r\n/g, '\n'));
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
if (Object.keys(state.outputs || {}).filter(name => name.endsWith('.html')).length !== 13) errors.push('Expected 13 generated HTML pages.');
if (errors.length) {
  console.error(errors.join('\n') + '\nRun npm run build, review the result, and include the updated generated files.');
  process.exit(1);
}
console.log('Verified ' + files + ' source and generated files. Static deployment artifacts are current.');
