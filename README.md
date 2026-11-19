# Realworld Labs website

Static, multi-page product website. The published files are in `public/`.

## Local preview

Run `npm run build` after editing content or templates, then `npm run dev`.
Open http://localhost:3000/ .

## Content and templates

- `content/hardware.json`: RealHand product content for L6, O6, L20, L30, and P7.
- `content/realstudio.json`: capabilities, independent editions, and feature matrix from the supplied new PDFs.
- `content/blog-latest.json`: the Agent as Policy research article and its publication metadata.
- `content/blog-jade.json`: the JADE research article, manuscript-derived figures/tables, and four real-robot demonstrations.
- `scripts/blog_content.py`: loads all `content/blog-*.json` entries by publication date; the newest appears on the homepage and every entry gets its own article page.
- `scripts/build_site.py`: shared layout and static page templates.
- `scripts/site_metadata.py`: canonical/share/schema metadata, discovery files, asset fingerprints, and build state.
- `scripts/site_experience.py`: product artwork, conceptual ecosystem data, and Coming soon pages.
- `public/ecosystem.css` and `public/ecosystem.js`: branded product previews and the interactive homepage ecosystem. Supports layer filtering, product details, drag perspective, a guided tour, keyboard navigation, and reduced motion.
- `public/pages.css` and `public/pages.js`: shared responsive styling and client interactions.

Build with Python 3.9 or newer; there are no third-party build dependencies.
Vercel serves `public/` directly. Each product and blog route has its own `index.html`.
The generated HTML is tracked, so deployment does not require a Python runtime.

All contact links use sales@realworldlabs.com.

Supplied RealStudio PDFs are content references only. Do not copy them into public/ or link them as downloads; present the product information as native webpage content.

## Launch validation

`npm run build` generates all 14 HTML pages, 13 canonical sitemap entries, robots.txt, the browser manifest, structured metadata, and fingerprinted CSS/JS. It validates the result before recording `content/build-state.json`.

- `npm run check`: validate metadata, share images, internal links and anchors, optimized image records, and routing settings.
- `npm run verify:build`: verify source and generated-file hashes using Node only. Vercel runs this command before deployment; stale or missing generated files fail deployment. The platform-processed `vercel.json` is excluded from byte hashing because Vercel can rewrite it before this step; `npm run build` and `npm run check` still validate its routing rules.
- `node scripts/check_build.test.mjs`: regression checks for platform config rewrites, line endings, and stale or missing site files, including research content and demo videos.
- `npm run dev`: serve the generated site locally with the custom HTTP 404 page, asset MIME types, cache classes, and MP4 byte-range requests for seeking.

After source changes, rebuild and include both the generated `public/` files and `content/build-state.json`. The deployment does not need Python.

## Sharing, browser icons, and image encoding

Each public page has a dedicated 1200 × 630 PNG in `public/assets/share/`. The artwork uses the existing brand and product assets; RealStudio uses the abstract software workflow.

- `scripts/share_cards.py`: editable HTML/SVG sharing-card source.
- `scripts/render_share_cards.py`: optional PNG and browser-icon renderer; requires `websocket-client`, the local preview, and an isolated Chromium debug session at localhost:9228. Use repeatable --key arguments to update selected cards without touching other artwork or icons.
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
- Each article has its own author, publication date, share image, and structured metadata. The Agent as Policy article links the official RoboDojo Agent leaderboard; the JADE article uses the supplied manuscript and does not expose the source PDF as a download.
- Research figures, posters, and demo videos are tracked in the deployment manifest. Videos use native controls, playsinline, and preload="none"; the four JADE clips retain their original H.264 video streams with fast-start MP4 metadata.

After deployment, verify the actual domain/TLS, canonical redirects, share-image URLs, and an unknown URL returning the custom body with HTTP 404. Submit `/sitemap.xml` in the owner's Search Console account after domain verification.

Vercel preview deployments normally receive its noindex header. A custom domain assigned to a Git branch requires a separate noindex rule; keep production crawlable.

References: [Vercel headers](https://vercel.com/docs/project-configuration/vercel-json#headers), [Vercel custom 404](https://vercel.com/kb/guide/custom-404-page), [Google sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap), [Open Graph](https://ogp.me/).
