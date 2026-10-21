# Lehi Tree Pros local release

Prepared October 21, 2026 on local branch `release/lehi-image-seo`, based on `main` at `1e5830c5d7144fb16b20d96e3dda6d9f7e0d5f9e`. Implementation commit: `d030052` (the report is recorded in a follow-up documentation commit). Nothing was pushed, published, deployed or changed in Cloudflare/GHL.

## Scope and exclusions

The release includes the corrected shared generator, required modules/templates/CSS, named Lehi config/content, image manifest, every optimized derivative, internal license records, optional optimizer and necessary tests/documentation. Other-site pending files, backup generator, six full-size originals, screenshots, old audits/test artifacts, frozen archives and preview builds are not added. Existing tracked legacy files are inherited unchanged; this is not a repository cleanup. No root generated HTML is overwritten or committed as a maintained build; Cloudflare must generate and publish `output/`.

**Image-count correction:** there are 33 optimized images: **30 WebP and 3 JPEG social-sharing images**, not 33 WebP. All 33 are included. The three JPEGs deliberately preserve broad social-sharing compatibility; none was converted or omitted. Their dimensions and byte counts match the manifest; build copies are byte-identical to source derivatives.

Lehi reviews are `disabled`, and sample prose is removed from its configuration. Reusable preview rendering and negative-test markers remain in source/tests; synthetic review text exists only in regression fixtures. No sample reviews, fictional testimonials or Review/AggregateRating schema appear in production output. Internal image provenance/license/caption fields are preserved, with no visible image credits.

## Clean-checkout verification

Created a separate local clone of the committed branch at `/tmp/lehi-release-clean-aqslgfp_/repo`; it was clean and had no output directory or original photos before building. Ran the **exact** Cloudflare command from its repository root:

```sh
python3 scripts/generate_site.py lehi-tree-pros
```

The command succeeded with system Python 3.9 and no dependency installation. Then:

- All **21 automated tests passed**, including both real Pillow encoder tests using the existing optional test environment. Tests cover phone placeholders/links, unchanged GHL form, canonical/sitemap/internal URL consistency, sample-review exclusion/preview gating, invalid build rejection, media behavior and exact public inventory.
- `python3 scripts/validate_production.py lehi-tree-pros` passed: 12 pages, 11 on-page image placements and 12 social-image references. Existing contact-page two-H1 warning remains; no errors.
- Confirmed `(385) 217-5381`, `tel:+13852175381` and `https://api.leadconnectorhq.com/widget/form/eeYobFkzVx8OwxuT8GmM` unchanged. No stale number, Tally form or unresolved placeholder appears in generated HTML.
- All canonicals/sitemap/internal page links use extensionless Lehi URLs, with home `/`; physical HTML filenames remain unchanged. Registered structured-data page URLs are normalized. Robots allows crawling and references the correct HTTPS sitemap; production has no noindex/nofollow directives.
- Output contains **exactly 49 public files** listed below: 12 HTML pages, CSS/JS, robots/sitemap, 30 WebP and 3 JPEG. No source code, configs, docs, licenses, originals, tests, credentials or Git files are included. Optimized image bytes are checked against the manifest.
- Credential-pattern scan of the prepared source additions passed; no private keys, token patterns or hardcoded credential assignments were found. Public phone/form IDs and public license/source URLs are intentional business/source data.
- Clean checkout remained clean after generation/tests (generated output and bytecode are ignored). Other-site configs/content and original published root HTML in the working repository remain unchanged.

Responsive Chrome checks: **120 page/viewport/DPR cases passed** from the clean checkout. All images and local sharing assets decoded; declared responsive sizes matched actual image boxes within 1 CSS pixel; no horizontal overflow, visible image credits, page errors or HTTP failures. Public clean routes returned 200 with correct canonical tags; mobile navigation, GHL/call links and production review/indexing exclusions passed. External requests were blocked. Browser artifacts remain outside Git at `/tmp/lehi-release-clean-browser/`.

## Build settings and outstanding risks

Expected Cloudflare Pages settings: Framework **None**; root **repository root**; build **`python3 scripts/generate_site.py lehi-tree-pros`**; output **`output`**. Python **3.9+** is required; verify no incompatible version override. Normal generation requires no Pillow, Playwright, Chrome, npm, API keys or photo downloads. Optional test/optimization requirements are separate. Restoring licensed originals and verifying original hashes is necessary only for future reoptimization.

The release builds locally, but the real Cloudflare project, production branch, custom-domain binding, build/deploy configuration and duplicate Pages/Workers triggers remain unverified. Previously observed source-file exposure on the live host is unresolved. Only the reviewed `output` may be served, never the repository root or stale root HTML. Verify existing redirects and account-side indexing headers before/after an approved deployment. GHL forwarding, submissions and CRM workflows were not exercised. Existing business claims/hours and the contact H1 issue are preserved rather than silently changed.

Pushing this branch could trigger preview or other Git integrations. **No push or infrastructure action is approved. Stop for owner review.** Earlier `.deployment` archives and old release hashes are superseded and must not be used. The local branch has no new deployment workflow or Cloudflare configuration.

## Complete changed/added file list

The following 58 files comprise the scoped release relative to main (including this report); all other inherited tracked files remain unchanged.

```text
.gitignore
AGENTS.md
assets/images/lehi-tree-pros/licenses/README.md
config/config-lehi-tree-pros.json
config/content-lehi-tree-pros.json
config/images-lehi-tree-pros.json
css/styles.css
docs/image-reviews.md
docs/lehi-release.md
images/optimized/lehi-tree-pros/emergency-tree-service-storm-damage-1200.webp
images/optimized/lehi-tree-pros/emergency-tree-service-storm-damage-1600.webp
images/optimized/lehi-tree-pros/emergency-tree-service-storm-damage-400.webp
images/optimized/lehi-tree-pros/emergency-tree-service-storm-damage-600.webp
images/optimized/lehi-tree-pros/emergency-tree-service-storm-damage-800.webp
images/optimized/lehi-tree-pros/emergency-tree-service-storm-damage-social-1200.jpg
images/optimized/lehi-tree-pros/general-tree-care-orchard-1200.webp
images/optimized/lehi-tree-pros/general-tree-care-orchard-1600.webp
images/optimized/lehi-tree-pros/general-tree-care-orchard-400.webp
images/optimized/lehi-tree-pros/general-tree-care-orchard-600.webp
images/optimized/lehi-tree-pros/general-tree-care-orchard-800.webp
images/optimized/lehi-tree-pros/stump-grinding-equipment-1200.webp
images/optimized/lehi-tree-pros/stump-grinding-equipment-1600.webp
images/optimized/lehi-tree-pros/stump-grinding-equipment-400.webp
images/optimized/lehi-tree-pros/stump-grinding-equipment-600.webp
images/optimized/lehi-tree-pros/stump-grinding-equipment-800.webp
images/optimized/lehi-tree-pros/stump-grinding-equipment-social-1200.jpg
images/optimized/lehi-tree-pros/tree-pruning-orchard-400.webp
images/optimized/lehi-tree-pros/tree-pruning-orchard-600.webp
images/optimized/lehi-tree-pros/tree-pruning-orchard-800.webp
images/optimized/lehi-tree-pros/tree-removal-chainsaw-1200.webp
images/optimized/lehi-tree-pros/tree-removal-chainsaw-1600.webp
images/optimized/lehi-tree-pros/tree-removal-chainsaw-400.webp
images/optimized/lehi-tree-pros/tree-removal-chainsaw-600.webp
images/optimized/lehi-tree-pros/tree-removal-chainsaw-800.webp
images/optimized/lehi-tree-pros/tree-removal-chainsaw-social-1200.jpg
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-400.webp
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-600.webp
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-800.webp
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-card-320.webp
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-card-400.webp
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-card-600.webp
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-card-800.webp
requirements-browser-tests.txt
requirements-images.txt
scripts/generate_site.py
scripts/optimize_images.py
scripts/preview_site.py
scripts/site_media.py
scripts/site_urls.py
scripts/validate_production.py
templates/home.html
templates/service.html
tests/browser_media.py
tests/test_image_optimizer.py
tests/test_production_preflight.py
tests/test_release_artifact.py
tests/test_site_media.py
tests/test_site_urls.py
```

## Complete generated public file list

These 49 files are generated by the build and are not committed as an `output/` snapshot.

```text
about.html
contact.html
css/styles.css
emergency-tree-service.html
faq.html
images/optimized/lehi-tree-pros/emergency-tree-service-storm-damage-1200.webp
images/optimized/lehi-tree-pros/emergency-tree-service-storm-damage-1600.webp
images/optimized/lehi-tree-pros/emergency-tree-service-storm-damage-400.webp
images/optimized/lehi-tree-pros/emergency-tree-service-storm-damage-600.webp
images/optimized/lehi-tree-pros/emergency-tree-service-storm-damage-800.webp
images/optimized/lehi-tree-pros/emergency-tree-service-storm-damage-social-1200.jpg
images/optimized/lehi-tree-pros/general-tree-care-orchard-1200.webp
images/optimized/lehi-tree-pros/general-tree-care-orchard-1600.webp
images/optimized/lehi-tree-pros/general-tree-care-orchard-400.webp
images/optimized/lehi-tree-pros/general-tree-care-orchard-600.webp
images/optimized/lehi-tree-pros/general-tree-care-orchard-800.webp
images/optimized/lehi-tree-pros/stump-grinding-equipment-1200.webp
images/optimized/lehi-tree-pros/stump-grinding-equipment-1600.webp
images/optimized/lehi-tree-pros/stump-grinding-equipment-400.webp
images/optimized/lehi-tree-pros/stump-grinding-equipment-600.webp
images/optimized/lehi-tree-pros/stump-grinding-equipment-800.webp
images/optimized/lehi-tree-pros/stump-grinding-equipment-social-1200.jpg
images/optimized/lehi-tree-pros/tree-pruning-orchard-400.webp
images/optimized/lehi-tree-pros/tree-pruning-orchard-600.webp
images/optimized/lehi-tree-pros/tree-pruning-orchard-800.webp
images/optimized/lehi-tree-pros/tree-removal-chainsaw-1200.webp
images/optimized/lehi-tree-pros/tree-removal-chainsaw-1600.webp
images/optimized/lehi-tree-pros/tree-removal-chainsaw-400.webp
images/optimized/lehi-tree-pros/tree-removal-chainsaw-600.webp
images/optimized/lehi-tree-pros/tree-removal-chainsaw-800.webp
images/optimized/lehi-tree-pros/tree-removal-chainsaw-social-1200.jpg
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-400.webp
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-600.webp
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-800.webp
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-card-320.webp
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-card-400.webp
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-card-600.webp
images/optimized/lehi-tree-pros/tree-trimming-pole-saw-card-800.webp
index.html
js/main.js
robots.txt
sitemap.xml
stump-grinding.html
tree-removal.html
tree-service-american-fork.html
tree-service-eagle-mountain.html
tree-service-lindon.html
tree-service-saratoga-springs.html
tree-trimming.html
```
