# Reusable images and homepage reviews

The Lehi release is local only. Do not push, publish, deploy, change GHL or change Cloudflare without explicit owner approval. Other sites and Bend are excluded from this release.

## Generate and inspect

```sh
python3 scripts/generate_site.py lehi-tree-pros
python3 scripts/validate_production.py lehi-tree-pros
python3 scripts/preview_site.py lehi-tree-pros --port 8000
```

Open http://localhost:8000/. Generation requires an explicit slug and replaces `output/`. The preview server resolves extensionless public routes to physical HTML files on loopback; it never deploys anything. The production build uses Python 3.9+ and only the standard library. No photo download, image encoder, API key, Node or browser is required. Cloudflare Pages should run the generator from repository root and publish only `output`, never the authoring root. Root HTML and earlier frozen deployment archives are stale.

`--preview` on generation adds `noindex, nofollow` to every page; never publish that output. **Lehi release reviews are disabled and contain no example review text**, even in preview. The reusable sample mode is regression-tested with test-only synthetic fixtures.

## Image contract

Enable `images.useImages` and set `images.manifest` to the site manifest. Version 1 manifests have `assetDirectory` under `images/optimized/<site>`, default `widths`, an `images` dictionary and filename-keyed `placements`.

Each image records its licensed `source` (URL, download URL, creator, license, license URL, terms, verification date), internal illustrative caption, original path, original dimensions/hash, descriptive filename stem, natural alt text, modification history and variant paths/dimensions/byte counts. Keep complete provenance even when originals are excluded from Git. Source records: [Lehi manifest](../config/images-lehi-tree-pros.json) and [license records](../assets/images/lehi-tree-pros/licenses/README.md).

Homepage slots are `hero`, `about`, and `service:<configured-service-slug>`; service slots are `main` and `detail`. Placements use physical filenames, regardless of public URL style. Invalid placements, unsafe paths, missing alt or missing derivatives fail before replacing output. Builds copy referenced derivatives only; originals and rights/config documents stay outside output. Legacy files outside `images/optimized` also copy, so inspect output inventory before release.

Lehi uses six licensed illustrative photos, **30 WebP variants and three 1200×630 JPEG sharing images**. Four sources use the Pexels License and two use CC0; recorded terms permit commercial use and modification without visible attribution. Never imply stock photos show Lehi crews or completed Lehi jobs. Do not remove attribution required by future licenses. The shared renderer emits no captions, photographer credits, source links or disclaimers; full records stay internal.

Rendered images have escaped natural alt text, explicit dimensions, responsive srcset/sizes and async decoding. The homepage hero is eager/high priority; other placements are lazy. Preserve descriptive filenames and avoid location claims in alt text. CSS and `sizes` expressions must remain synchronized; browser checks compare actual boxes with declared sizes within 1px across breakpoints.

Optional `renditions` support named `widths`, positive-integer `aspectRatio`, normalized `cropCenter`, `format` (`webp`/`jpeg`) and `quality`. The optimizer crops without stretching or upscaling, strips EXIF/GPS and records dimensions/bytes. A `card` rendition is selected automatically for service cards; the original-aspect portrait remains on service pages.

`social.default` and optional `social.pages` select image IDs by physical page filename. If omitted, the homepage hero is the default. A named `social` rendition is preferred; otherwise an existing variant is selected. The generator emits absolute og:image/twitter:image URLs on the configured domain, alt text, dimensions, MIME and twitter:card. Sites without enabled media emit no image tags. Sharing metadata is independent of review preview mode.

## Reoptimization

Originals are retained locally but deliberately excluded from this release. In a clean checkout, restore them from local storage or recorded licensed download URLs, verify their manifest SHA256 hashes, then:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-images.txt
.venv/bin/python scripts/optimize_images.py config/images-lehi-tree-pros.json --quality 70
```

Pillow is optional and not part of the Cloudflare build. Review derivatives and manifest changes before committing. Do not delete retained originals or source/license records. Reoptimization is unnecessary for normal builds.

## Reviews contract

Homepage only: missing settings or `reviews.mode: "disabled"` renders nothing. Lehi ships disabled. The reusable `sample` mode requires supplied items and `--preview`, clearly labels demonstrations and fictional authors, omits ratings, and never emits review schema. Synthetic examples belong in tests or deliberately separate local authoring data, not Lehi's release config.

For authentic reviews later, use `google` mode with verified `author` (first name/initial), unedited `text`, HTTPS Google `sourceUrl`, and optional integer `rating` from 1–5. The component includes Google/source attribution and no Review/AggregateRating schema. This is a display contract, not an API integration or proof of authenticity. Verify review rights and Google display rules before enabling. No service-page review sections.

## Public URL styles

`publicUrlStyle` accepts `html` (default) or `extensionless` (Lehi). `scripts/site_urls.py` normalizes registered quoted local page URLs in navigation, breadcrumbs, canonical/OG attributes and JSON-LD after placeholder rendering; sitemap uses the same map. Physical `.html` filenames and manifest keys are preserved. External URLs, phone/form links, assets, queries and fragments remain intact. This setting does not configure production redirects. Other sites are not opted in automatically.

## Tests and release

Generate production first, then:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/validate_production.py lehi-tree-pros
```

Install `requirements-images.txt` in a test environment for both real-encoder tests; otherwise those two tests skip. The inventory test requires exactly 49 public files, including all 33 derivatives, and excludes source/config/license/original/test files. Contact's existing two H1s remain a documented warning. Checks do not prove GHL call forwarding, form submission or CRM behavior.

For optional browser testing install `requirements-browser-tests.txt` and use:

```sh
python tests/browser_media.py --production --chrome '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
```

Without an existing Chrome executable, install Playwright Chromium separately. Browser checks request only localhost, block external traffic, test 120 page/viewport/DPR cases, decode images/sharing images, check layout/sizes/navigation/contacts/canonicals and reject sample content in production. Screenshots/results go to `/tmp` and must not be committed.

See [local release report](lehi-release.md) for the file list, clean-checkout results and production risks. New site rollout requires owner review. Never use the Lehi-root publishing script for another site.
