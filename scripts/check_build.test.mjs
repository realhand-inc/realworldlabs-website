// Exercise the real deployment command against an isolated copy of its recorded files.
import { strict as assert } from 'node:assert';
import { readFileSync, writeFileSync, copyFileSync, mkdirSync, mkdtempSync, rmSync, realpathSync } from 'node:fs';
import { resolve, dirname, extname, join, relative, isAbsolute } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const state = JSON.parse(readFileSync(join(root, 'content/build-state.json'), 'utf8'));

let passed = 0;
const t = { async test(name, run) {
  await run();
  passed++;
  console.log('PASS ' + name);
} };
{
  assert.equal(Object.prototype.hasOwnProperty.call(state.inputs, 'vercel.json'), false,
    'Deployment configuration must be validated by rules, not byte hashed.');
  const temporaryBase = realpathSync(tmpdir());
  const fixture = mkdtempSync(join(temporaryBase, 'rwl-deploy-check-'));
  try {
    const names = new Set(['vercel.json', 'content/build-state.json',
      ...Object.keys(state.inputs), ...Object.keys(state.outputs)]);
    for (const name of names) {
      const destination = resolve(fixture, name);
      const fromFixture = relative(fixture, destination);
      assert.ok(!isAbsolute(fromFixture) && !fromFixture.startsWith('..'));
      mkdirSync(dirname(destination), { recursive: true });
      copyFileSync(resolve(root, name), destination);
    }
    const verify = () => {
      const result = spawnSync(process.execPath, ['scripts/check_build.mjs'], {
        cwd: fixture, encoding: 'utf8',
      });
      assert.ifError(result.error);
      return { status: result.status, log: result.stdout + result.stderr };
    };
    const change = async (name, content, run) => {
      const path = join(fixture, name);
      const original = readFileSync(path);
      try {
        if (content === null) rmSync(path);
        else writeFileSync(path, content);
        await run();
      } finally { writeFileSync(path, original); }
    };

    await t.test('unchanged checkout passes', () => {
      const result = verify();
      assert.equal(result.status, 0, result.log);
    });
    const attributes = readFileSync(join(fixture, '.gitattributes'), 'utf8').replace(/\r\n/g, '\n');
    for (const [label, content] of [['LF', attributes], ['CRLF', attributes.replace(/\n/g, '\r\n')]]) {
      await t.test('.gitattributes with ' + label + ' line endings passes', async () => {
        await change('.gitattributes', content, () => {
          const result = verify();
          assert.equal(result.status, 0, result.log);
        });
      });
    }
    await t.test('Linux checkout with LF text files passes', () => {
      const originals = new Map();
      const extensions = new Set(['.py','.json','.js','.mjs','.css','.html','.xml','.txt','.svg','.webmanifest']);
      try {
        for (const name of names) {
          // These fingerprinted assets are explicitly -text in .gitattributes.
          if (name.startsWith('public/assets/build/')) continue;
          if (name !== '.gitattributes' && !extensions.has(extname(name))) continue;
          const path = join(fixture, name);
          const original = readFileSync(path);
          originals.set(path, original);
          writeFileSync(path, original.toString('utf8').replace(/\r\n/g, '\n'));
        }
        const result = verify();
        assert.equal(result.status, 0, result.log);
      } finally {
        for (const [path, original] of originals) writeFileSync(path, original);
      }
    });
    await t.test('changed .gitattributes rules still fail', async () => {
      await change('.gitattributes', attributes + '/public/assets/build/* text\n', () => {
        const result = verify();
        assert.equal(result.status, 1);
        assert.match(result.log, /Changed source: \.gitattributes/);
      });
    });
    await t.test('Vercel can reserialize and extend vercel.json', async () => {
      const config = JSON.parse(readFileSync(join(fixture, 'vercel.json'), 'utf8'));
      config.framework = null;
      await change('vercel.json', JSON.stringify(config), () => {
        const result = verify();
        assert.equal(result.status, 0, result.log);
      });
    });
    await t.test('changed page source still fails', async () => {
      await change('public/pages.css', '/* stale deployment source */', () => {
        const result = verify();
        assert.equal(result.status, 1);
        assert.match(result.log, /Changed source: public\/pages\.css/);
      });
    });
    await t.test('changed research article content still fails', async () => {
      await change('content/blog-jade.json', '{}', () => {
        const result = verify();
        assert.equal(result.status, 1);
        assert.match(result.log, /Changed source: content\/blog-jade\.json/);
      });
    });
    await t.test('missing research demo video still fails', async () => {
      const video = Object.keys(state.outputs).find(name =>
        name.startsWith('public/assets/blog/jade/videos/') && name.endsWith('.mp4'));
      assert.ok(video, 'Research videos must be recorded as deployment artifacts.');
      await change(video, null, () => {
        const result = verify();
        assert.equal(result.status, 1);
        assert.ok(result.log.includes('Missing output: ' + video), result.log);
      });
    });
    await t.test('changed generated HTML still fails', async () => {
      await change('public/index.html', '<h1>Stale output</h1>', () => {
        const result = verify();
        assert.equal(result.status, 1);
        assert.match(result.log, /Changed output: public\/index\.html/);
      });
    });
    await t.test('missing fingerprinted CSS still fails', async () => {
      const css = Object.keys(state.outputs).find(name =>
        name.startsWith('public/assets/build/') && name.endsWith('.css'));
      assert.ok(css);
      await change(css, null, () => {
        const result = verify();
        assert.equal(result.status, 1);
        assert.ok(result.log.includes('Missing output: ' + css), result.log);
      });
    });
  } finally {
    // Only remove the exact directory created above, directly inside the system temp dir.
    assert.equal(dirname(realpathSync(fixture)), temporaryBase);
    assert.ok(relative(temporaryBase, fixture).startsWith('rwl-deploy-check-'));
    rmSync(fixture, { recursive: true, force: true });
  }
}
console.log('Passed ' + passed + ' deployment regression checks.');
