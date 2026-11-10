# Realworld Labs website

Static, multi-page product website. The published files are in `public/`.

## Local preview

Run `npm run build` after editing content or templates, then `npm run dev`.
Open http://localhost:3000/ .

## Content and templates

- `content/hardware.json`: RealHand product content for L6, O6, L20, L30, and P7.
- `content/realstudio.json`: capabilities, independent editions, and feature matrix from the supplied new PDFs.
- `content/blog-latest.json`: the latest RealHand article and its original publication metadata.
- `scripts/build_site.py`: shared layout and static page templates.
- `scripts/site_metadata.py`: canonical/share/schema metadata, discovery files, asset fingerprints, and build state.
- `scripts/site_experience.py`: product artwork, conceptual ecosystem data, and Coming soon pages.
- `public/ecosystem.css` and `public/ecosystem.js`: branded product previews and the interactive homepage ecosystem. Supports layer filtering, product details, drag perspective, a guided tour, keyboard navigation, and reduced motion.
- `public/pages.css` and `public/pages.js`: shared responsive styling and client interactions.

Build with Python 3.9 or newer; there are no third-party build dependencies.
Vercel serves `public/` directly. Each product and blog route has its own `index.html`.
The generated HTML is tracked, so deployment does not require a Python runtime.

All contact links use sales@realworldlabs.com.

## Launch validation

`npm run build` generates all 13 HTML pages, 12 canonical sitemap entries, robots.txt, the browser manifest, structured metadata, and fingerprinted CSS/JS. It validates the result before recording `content/build-state.json`.

- `npm run check`: validate metadata, share images, internal links and anchors, optimized image records, and routing settings.
- `npm run verify:build`: verify source and generated-file hashes using Node only. Vercel runs this command before deployment; stale or missing generated files fail deployment.
- `npm run dev`: serve the generated site locally with the custom HTTP 404 page, asset MIME types, and cache classes.

After source changes, rebuild and include both the generated `public/` files and `content/build-state.json`. The deployment does not need Python.

## Sharing, browser icons, and image encoding

Each public page has a dedicated 1200 × 630 PNG in `public/assets/share/`. The artwork uses the existing brand and product assets; RealStudio uses the abstract software workflow.

- `scripts/share_cards.py`: editable HTML/SVG sharing-card source.
- `scripts/render_share_cards.py`: optional PNG and browser-icon renderer; requires `websocket-client`, the local preview, and an isolated Chromium debug session at localhost:9228.
- `scripts/optimize_images.py`: optional lossless WebP encoder; requires Pillow with WebP support. It checks exact decoded RGBA pixels and records source/output hashes in `content/image-optimizations.json`.

Run image encoding when its original PNG sources change, or render the sharing cards when their copy/artwork changes, then run `npm run build`. The normal build uses only Python's standard library.

To open an isolated renderer on Windows while the preview is running:

```powershell
$taskBrowserProfile = Join-Path $env:TEMP 'rwl-share-artwork'
Start-Process -FilePath "$env:ProgramFiles\Google\Chrome\Application\chrome.exe" -WindowStyle Hidden -ArgumentList @('--headless=new','--remote-debugging-port=9228','--remote-allow-origins=http://localhost:9228',('--user-data-dir="' + $taskBrowserProfile + '"'),'about:blank')
python scripts/render_share_cards.py
npm run build
```

## Production behavior

- Canonical URLs and the sitemap use `https://www.realworldlabs.com/` with trailing slashes.
- The custom 404 has `noindex` and no homepage canonical. There is no catch-all rewrite to the homepage.
- HTML revalidates; replaceable assets use a short cache; content-fingerprinted CSS/JS are immutable.
- The blog's structured data preserves the original author, publication date, and source attribution.

After deployment, verify the actual domain/TLS, canonical redirects, share-image URLs, and an unknown URL returning the custom body with HTTP 404. Submit `/sitemap.xml` in the owner's Search Console account after domain verification.

Vercel preview deployments normally receive its noindex header. A custom domain assigned to a Git branch requires a separate noindex rule; keep production crawlable.

References: [Vercel headers](https://vercel.com/docs/project-configuration/vercel-json#headers), [Vercel custom 404](https://vercel.com/kb/guide/custom-404-page), [Google sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap), [Open Graph](https://ogp.me/).
