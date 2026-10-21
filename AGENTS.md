# Rank + Rent project instructions

## Authority and scope

Read this file before working in this repository. The owner’s current instructions take precedence. Actual source code is authoritative for technical behavior; project notes describe intent or historical state, not proof of current deployment.

Context source: `../Rank_and_Rent_Work_Handoff.md`, prepared October 8, 2026. Read it for wider portfolio and operating context when available. This file records a local inspection on that date. Recheck Git state, configs, and deployment settings before acting; do not assume the snapshot remains current.

**Bend Foundation Repair is excluded from the current SEO image/homepage reviews implementation.** Do not change its source, generated files, assets, repository, or deployment as part of that work. Approved targets are Lehi Tree Pros, Irvine Drywall, Sammamish Drywall, and Carmel Spray Foam. Carmel Concrete is not an approved target either.

## Goals and operating principles

- Build residential local-service lead-generation websites, rank them in organic search and maps where eligible, capture calls/forms, and rent them to providers for monthly revenue. Do not assume sites are rented or earning income.
- Scale to hundreds of sites with reusable automation and minimal maintenance. Fix recurring issues in the generator, shared templates, CSS/JS, or reusable tooling. Site facts and content belong in per-site data. Never use manual generated-HTML edits as the maintained solution.
- Prefer free tools, free hosting tiers, and properly licensed free images. Disclose costs before introducing paid services, API usage, subscriptions, or paid directory listings.
- Market selection preferences: one primary city per site, residential services, city population at least 50,000, at least five potential providers/renters, relatively low competition, and high-value jobs ($5,000+ preferred; over $1,000 desirable; over $500 minimum). Avoid markets with a strong competitor owning the exact city/service domain. Nearby location pages already exist; do not remove them merely because there is one primary city.
- GHL is the standard for forms, public tracking numbers, contacts, opportunities, workflows, and email/SMS. GitHub, Cloudflare, and Porkbun are the established infrastructure.
- Work autonomously on authorized, reversible work. Ask only for missing facts, meaningful decisions, necessary access, or approval required by the environment. Do not invent business facts or claim unobserved outcomes.

## Repository map and implementation

Local root at inspection: `/Users/ianscott/Desktop/Lack Pard Rank + Rent/Local SEO Template`.

| Path | Purpose |
| --- | --- |
| `scripts/generate_site.py` | Active Python static generator; standard library only |
| `scripts/publish_site.py` | Copies generated output into this repository’s root; not a remote deployer |
| `scripts/generate_site-backup.py` | Older generator snapshot; do not treat as active CLI documentation |
| `config/config-<slug>.json` | Site facts, services, locations, optional image manifest and homepage reviews |
| `config/content-<slug>.json` | Page copy, service/location FAQs, metadata |
| `config/config.json`, `config/content.json` | Default legacy Lehi inputs; contact data differs from named Lehi config |
| `templates/` | Shared HTML layouts |
| `css/styles.css`, `js/main.js` | Shared styling, navigation, FAQ and other browser behavior |
| `images/` | Legacy shared assets and `optimized/<site>/` WebP libraries; builds copy only manifest-used optimized assets |
| `assets/images/<site>/` | Licensed original photos and rights records; never copied into site output |
| `scripts/site_media.py`, `scripts/optimize_images.py` | Manifest validation/rendering and optional Pillow optimization |
| `config/images-<slug>.json` | Source/license records, local originals, derivative dimensions and page/section placements |
| `tests/` | Automated media/build regression checks and optional local Playwright browser checks |
| `output/` | Disposable build destination; ignored by Git |
| Root HTML, sitemap, robots | Previously published Lehi build; not generator source |
| `docs/` | Architecture, project/content/SEO/design standards, roadmap, changelog |
| `prompts/site-generation.md`, `agent/content-generator.md`, `variables.md` | Supporting authoring references; some instructions/shapes are stale |

The active generator accepts a site slug, not an arbitrary config path. It loads matching config/content files, constructs placeholder variables, and performs string replacement for up to three passes. It does not use a template engine, escape all inserted HTML/JSON values, or validate unresolved placeholders. Treat content as trusted authoring input and validate rendered output, especially quotes and special characters in structured data.

It deletes the entire shared `output/` directory, creates it again, copies `css/`, `js/`, and `images/`, then renders:

- `home.html` → `index.html`, plus about, contact, and FAQ;
- `service.html` once per configured service;
- `location.html` once per configured nearby city;
- `sitemap.xml` and `robots.txt` using the configured domain and generated page paths.

Each existing config has four services and four nearby cities, producing 12 HTML pages. Service/location generation loops over data, but homepage/navigation templates explicitly reference services 1–4. Supporting templates `city.html`, `blog.html`, `privacy.html`, and `404.html` are not generated by the active script.

Content service entries are matched by exact `name`; location entries by exact `city`. Missing matches fall back to incomplete/default copy. FAQ content must be an object with `headline`, `intro`, and `questions`, not the array shown in the older content-generator prompt. Consult existing named content JSON and the active generator for the real contract.

## Sites, configurations, and repository relationships

Every slug below has both `config/config-<slug>.json` and `config/content-<slug>.json`.

| Slug/site | Domain | Public phone in named config | GitHub repository |
| --- | --- | --- | --- |
| `lehi-tree-pros` / Lehi Tree Pros | `lehitreepros.com` | `(385) 217-5381` — owner verified October 21, 2026 | `https://github.com/ipscott1995-sudo/Lehi--Utah-Tree-Service.git` |
| `irvine-drywall` / Irvine Drywall | `drywallirvine.com` | `(949) 592-1961` | `https://github.com/ipscott1995-sudo/Irvine-Drywall.git` |
| `sammamish-drywall` / Sammamish Drywall | `sammamishdrywall.com` | `(425) 671-4854` | Exact repository URL not verified |
| `carmel-spray-foam` / Carmel Spray Foam | `carmelsprayfoam.com` | `(463) 223-3884` | `https://github.com/ipscott1995-sudo/Carmel-Spray-Foam.git` |
| `carmel-concrete` / Carmel Concrete Paving | `carmelconcretepaving.com` | `(317) 555-0198` placeholder | Not verified; do not assume launched |

This template workspace itself has the **Lehi GitHub remote**, on branch `main` at inspection. It is not an independently verified central-template repository. `../Lehi, Utah Tree Service` also points to that same remote. Determine which checkout is authoritative before committing/pushing.

Separate generated repositories were found at `../Generated Sites/Irvine-Drywall` and `../Generated Sites/Carmel-Spray-Foam`, with remotes listed above. No Sammamish checkout was located in the searched directories. These locations are outside this workspace’s writable root and may require permission for writes.

Services and location pages:

- Lehi: removal, trimming, stump grinding, emergency tree service; American Fork, Eagle Mountain, Lindon, Saratoga Springs.
- Irvine: installation, repair, finishing/texturing, replacement; Tustin, Costa Mesa, Newport Beach, Lake Forest. Patching and wall/ceiling repairs are broader-page topics, not separate configured pages.
- Sammamish: installation, repair, finishing/texturing, replacement; Issaquah, Redmond, Bellevue, Newcastle.
- Carmel Spray Foam: attic, crawl space, wall, removal/replacement; Fishers, Westfield, Noblesville, Zionsville.
- Carmel Concrete: driveways, patios, sidewalks, repair; Fishers, Westfield, Noblesville, Zionsville.

Bend is a separate legacy migration, not a config in this generator. Handoff-only references: `https://github.com/ipscott1995-sudo/Bend-Foundation-Repair.git`, local `/Users/ianscott/Bend-Foundation-Repair`, domain `https://www.bendfoundationrepair.com/`, static assets under `site/`. Those details were not verified during this template inspection. Preserve its existing extensionless routes and legacy redirects if a future separately authorized task concerns Bend.

## Configure, generate, test, and update

1. Inspect `git status --short`, branch, remotes, and relevant diffs first. Preserve all existing changes. At inspection, the active generator had an uncommitted slug-loading change; Irvine/Sammamish/Carmel Spray Foam config/content pairs and the backup generator were untracked. Do not discard or accidentally omit them.
2. Update shared source for shared behavior and matching named JSON files for site-specific data. Validate JSON, exact service/city matches, phone/form values, and safe relative output filenames. Domain values are bare hostnames; templates add `https://`.
3. Generate one site at a time from repository root:

   ```sh
   python3 scripts/generate_site.py lehi-tree-pros
   python3 scripts/generate_site.py irvine-drywall
   python3 scripts/generate_site.py sammamish-drywall
   python3 scripts/generate_site.py carmel-spray-foam
   ```

   These are alternative sequential builds, **not** a batch retaining all sites. Every command replaces `output/`. Preserve a reviewed site’s build in its correct destination before generating another. An explicit site slug is now required for both production and preview builds; missing slugs fail before modifying output. Legacy default contact data remains stale and is not loaded by the active CLI. Never run generation during a read-only inspection task.
4. Verify the generated site before publishing: expected pages, no unresolved `{{...}}`, valid HTML/JSON-LD, correct title/meta/H1/canonical/domain, sitemap/robots coverage, internal links, asset existence, phone/form links, and no unintended review schema. Preview desktop and mobile, including nav, sticky CTAs, and forms. For local preview, `python3 -m http.server 8000 --directory output` serves the build; stop it when done.
5. For image work, additionally check source licenses, alt text, dimensions, responsive behavior, file sizes, missing images, hero loading priority, and below-fold lazy loading. Use appropriate smoke/regression tests; no automated test suite or package/build tooling was found at inspection.
6. Publish only the reviewed output into the correct site checkout, inspect diffs there, stage intentional files, and commit when authorized. Fix problems at source, regenerate, and review again; do not maintain patches only in output.

`python3 scripts/publish_site.py` only copies `output/` to **this workspace root**. It replaces matching files and whole asset directories but does not remove obsolete HTML, select a site, verify domain, commit, push, or deploy. Because this workspace points to Lehi, do not use it to publish another site. It can also overwrite asset source folders; review provenance and backups before use. There is no implemented site-isolated build/deploy pipeline yet.

## GitHub and Cloudflare deployment

**Explicit owner approval is required before any action that could affect a live website. Never push to GitHub, trigger Cloudflare deployments, publish websites, or modify production infrastructure without the owner’s explicit approval.** Inspection, local code edits, and local tests are permitted within the authorized task. Complete local preparation and testing, show the owner what changed and the validation results, describe the proposed production action and affected sites, and request approval before executing it. Do not infer production approval from a general implementation request, the handoff’s historical deployment plan, or these procedural instructions.

No GitHub Actions workflows, Wrangler configuration, Cloudflare project mapping, or remote deployment automation were found in the inspected template and nearby generated repositories. Documentation describes Cloudflare Pages; the handoff mentions both Pages and Workers. Do not infer which currently hosts a site or assume a push triggers deployment.

Before any deployment:

1. Verify the destination checkout’s remote, branch, status, and deployed domain. Establish the site’s actual Cloudflare project, Pages/Workers mode, asset directory/build settings, and Git integration or direct-upload route using authenticated read-only inspection.
2. Review the full build diff and preserve existing routing, forms, SEO settings, domain configuration, and unrelated files. Do not copy template-only authoring files into an asset directory unintentionally.
3. Use the verified existing deployment mechanism. If Git-connected, push only the intended site commit to its configured branch and observe the Cloudflare build. If direct-deployed, use its verified project/config and secure authentication. Do not invent Wrangler commands or project names. Deployment authorization does not eliminate environmental approval requirements.
4. **Never reuse a Cloudflare build/deploy token across sites.** Keep site-specific credentials outside source control and chat. Use secure authentication/environment variables with appropriately scoped permissions.
5. Observe deployment completion, then verify the custom domain, representative pages, canonical URLs, assets, sitemap/robots, and call/form links. Confirm actual GHL submission/contact/opportunity behavior when authorized; avoid unnecessary production test leads. Report exactly what was observed.

Keep Porkbun/Cloudflare DNS changes separately scoped and preserve mail MX/TXT records. Historical Carmel parking-record conflict is not evidence of a current problem. Roll back with a reviewed prior build/commit through the actual deployment mechanism; never force-push or reset away user work.

## SEO, content, and schema

- Maintain static HTML, lightweight shared CSS/JS, responsive layouts, prominent phone/form CTAs, internal service/location links, unique page metadata, one H1, and accurate canonical URLs.
- Public URLs use per-site `publicUrlStyle` (`html` by default; `extensionless` for Lehi). `scripts/site_urls.py` maps registered page filenames to public links, canonicals, sitemap and JSON-LD without renaming physical HTML files or image-manifest keys. Lehi uses `/about`, etc., matching its previously observed live redirects; no live redirects were changed. Keep deployed routing under separate review.
- Write clear local copy for residential homeowners/property owners. Use keywords naturally; no stuffing or fabricated local facts, addresses, founders, experience, awards, certifications, licenses, GBP verification, reviews, or rankings.
- Use only accurate business/service/FAQ/breadcrumb schema when implemented. Current homepage/about/contact contain business JSON-LD; do not assume other schema exists merely because standards allow it. Never add fabricated `Review` or `AggregateRating` data.
- Existing standards target 15–25 FAQ questions, but actual configs have 6–7. Treat that as a documented gap, not a reason to invent answers or automatically expand scope.
- Shared templates currently contain “Residential and commercial service” and “Locally Owned”; these conflict with residential-only policy or require factual support. Generator hours are hardcoded Mon–Fri 7–7, Sat 8–5, Sun closed, differing from handoff citation hours. Do not silently change public business facts; resolve through site-specific data when authorized.
- Legacy prompt/roadmap mentions CallRail, an obsolete logistics/lead tracker, and an outdated FAQ JSON shape. Follow current GHL/business policy and active code instead.

## Reusable image and homepage review system

Implemented locally October 8, 2026 for Lehi only. Read `docs/image-reviews.md` for the manifest contract, optimization commands, review modes, tests, and rollout instructions. Lehi has six licensed illustrative photos, responsive WebP variants, homepage/service placements, and three sample review cards. Other sites remain opted out and were not regenerated or published. **Stop for owner review before applying the prototype to Irvine, Sammamish, or Carmel Spray Foam.**

Enable images with `images.useImages: true` and `images.manifest: "config/images-<slug>.json"`. The old `hero`/`service1`–`service4` image fields are still unused. Builds without media keep their existing layout with empty new slots and the homepage SVG fallback. Optimization requires optional Pillow; normal generation remains standard-library-only. Only manifest-referenced files in `images/optimized/` are copied into builds; originals/license records stay outside output.

`python3 scripts/generate_site.py lehi-tree-pros --preview` displays clearly labeled samples and adds `noindex, nofollow` to all generated HTML pages. Standard builds omit sample reviews and preview noindex. Review modes are `disabled`, `sample`, and `google`; the latter renders owner-supplied authentic review data with source links, not a Google API integration. No review/rating schema is emitted by this component. Never publish a preview build; production approval is still required for any publish/push/deployment.

Approved plan: start with Lehi, validate the shared implementation, then apply to Irvine, Sammamish, and Carmel Spray Foam. Preserve Bend exclusion and existing contact/SEO behavior.

- Source 5–8 relevant properly licensed images per site; owner has no photos. Prefer free commercial-use imagery and record source/license/attribution evidence. Do not extract arbitrary YouTube frames without reusable rights.
- Use local assets and a per-site manifest recording source URL, license/attribution, filename, page/section placement, subject/alt, and dimensions. Keep optimization and placement reusable; avoid copying every site’s image library into every build.
- Resize/compress to WebP, descriptive filenames, accurate natural alt text, explicit width/height, responsive `srcset`/sizes where useful, lazy loading below fold, and priority handling for the LCP hero. Consider image sitemap support when warranted. Never claim EXIF/geotagging inherently improves ranking.
- Place images contextually on homepage/service pages. Do not imply stock/AI imagery shows the business’s own crews or completed local jobs.
- Homepage-only reviews component, managed by per-site data. Three unmistakably labeled sample/example reviews for design preview; no real reviews currently supplied. Samples are gated behind `--preview` and omitted from standard builds; never present them as genuine endorsements or emit rating/review schema.
- Future Google integration requires authentic review text, attribution/source, reviewer first name/initial and rating, plus verification of applicable Google display/API rules at implementation time.

## GHL and lead operations

Current forms are external links via `business.formUrl`, not a native GHL embed/integration in the generator:

| Site | Form URL in named config | Handoff GHL location ID (not verified live) |
| --- | --- | --- |
| Lehi | `https://api.leadconnectorhq.com/widget/form/eeYobFkzVx8OwxuT8GmM` | Unknown |
| Irvine | `https://api.leadconnectorhq.com/widget/form/lfrh0t58Zh1rtmCwm1aw?notrack=true` | `gY59UYyK7No1sTNUPx95` |
| Sammamish | `https://link.apisystem.tech/widget/form/iM9ed7mS57or1xxQZaya` | `1IAjZcwWx8GaEfyluisd` |
| Carmel Spray Foam | `https://api.leadconnectorhq.com/widget/form/KjBCmDKJ4YfaGIynbpLn?notrack=true` | `Pyp27vxNu8cZUBTRajyb` |

Use `phoneDisplay` for readable numbers and `phoneTel` for `tel:` links. Preserve both together. Lehi named config/root HTML use `(385) 217-5381`, default config uses `(385) 534-4337` with Tally, and handoff citations report `(385) 483-2108` with a verification warning. Confirm the actual public GHL number with the owner/authenticated service before resolving this discrepancy. Carmel Concrete has placeholder phone/Tally values and is not production-ready by implication.

GHL subaccounts, contacts, `New Leads` opportunities, workflows, forwarding, SMS/email consent, and form setup are service-side configuration; no automation/API code for these was found here. Handoff reports prior Sammamish/Carmel contact/opportunity tests, not evidence of current operation. Never claim end-to-end lead capture solely because a form URL renders. Existing JS has a demo handler for `#contact-form` that displays success without sending data; do not reuse it as functional lead handling.

Future reusable GHL snapshots/custom values and call transcription are ideas, not implemented features. Verify pricing before enabling paid transcription or other services.

## Business records and production safety

- Primary business source of truth: `Rank_and_Rent_Business_Database`, `https://docs.google.com/spreadsheets/d/1N9YCOpmkg08WKZ41VtaxbbY2zJtKZC13qYAeMte426w/edit` (Sites, Infrastructure, Financials, Leads & Sales, Clients). Use authorized access; local inspection did not verify current values.
- Citations source: `https://docs.google.com/spreadsheets/d/1QNtSVpivakkgcNyAtjjGARrPz4N4KIf3QUeNsjVTPlM/edit`. Keep NAP consistent after verification; owner supplies missing addresses. Do not assume a citation address establishes GBP eligibility. Do not maintain the obsolete `Webiste Logistics Tracker` unless instructed.
- Never include passwords, tokens, API keys, recovery secrets, private keys, or other credentials in files, commits, chat, logs, screenshots, or generated output.
- Preserve unrelated edits, deployed URLs, lead paths, tracking data, and infrastructure. Do not force-push, delete assets, alter DNS, or mass-request indexing without appropriate task scope and review.
- Build and test before production writes. Review destination and diffs explicitly. Claim successful deployment or end-to-end behavior only after observing it at the real URL/service.
- Never push to GitHub, trigger Cloudflare deployments, publish websites, or modify production infrastructure without explicit owner approval. Show the prepared changes and local test results and request approval before any action that could affect a live website. Local inspection, edits, and tests do not authorize production actions.
- Keep changes at reusable source level and per-site data. Add documentation for new contracts so future sites inherit behavior without one-off edits. Do not change excluded sites indirectly through batch generation or deployment.

## Important unresolved information

Authoritative Lehi checkout versus central template repository strategy; Sammamish repository/local checkout; per-site Cloudflare projects, hosting mode, build/deploy settings and authentication; current GHL workflow/forwarding status; verified site-specific hours/business claims; image selections/licenses for the other three sites; actual live deployment parity. The existing contact template has two H1s; this was preserved and flagged during Lehi regression testing. These are uncertainties, not permission to guess or block unrelated authorized source work.

## Image presentation update — October 20, 2026

Owner requested removal of all visible photo captions, disclaimers, photographer names, source links and license credits. The shared image renderer now emits images without figcaptions. Keep complete source/creator/license/caption records internally in manifests and documentation. All six Lehi sources were rechecked: four Pexels License photos and two CC0 photos permit commercial website use without visible attribution. Future source selections must permit this presentation; do not strip attribution required by a different license or imply stock imagery is the business’s own work. Image alt text, filenames, responsive variants, dimensions and loading settings remain intact.


## Responsive/rendition/sharing maintenance update — October 20, 2026

Lehi’s shared renderer now has CSS-matched sizes hints; the browser tests compare declared slot widths with actual boxes across grid/sidebar breakpoints. Keep renderer expressions and CSS synchronized. The optional optimizer supports per-image `renditions` (aspectRatio, cropCenter, widths, format, quality); `card` renditions avoid downloading tall portraits only to crop them on small cards. Original portraits remain on service pages. Named social JPEG renditions provide 1200×630 sharing images while normal page photos remain WebP. The manifest `social.default` / `social.pages` chooses images, defaulting to the homepage hero when omitted. Generated og:image/twitter:image URLs use the current site domain; no social API or deployment is involved. See docs/image-reviews.md and the audit remediation section for the current contract and validation.

The orchard-photo implication was resolved through Lehi’s homepage heading/snippet data, with all source/license records retained. Do not apply these local Lehi changes to other site outputs without owner review. Production approval rules remain unchanged.


## Production deployment preparation — October 21, 2026

A standard Lehi build (no --preview) is prepared in output/ and frozen under ignored .deployment/lehi-tree-pros/. Read docs/lehi-media-review/production-readiness.md before any deployment action. Fifteen automated tests and 120 production browser cases passed; scripts/validate_production.py intentionally reports NOT READY because an older phone number remains in prose/meta descriptions on ten pages, also present on the live site. Live/current config phone CTAs agree on (385) 217-5381 and the existing GHL form; no phone/contact decision was made. Canonicals and sitemap loc values still use .html while live hosting redirects those URLs to extensionless paths; this existing conflict is preserved and flagged. The generator’s sitemap namespace was corrected locally to the standard http://www.sitemaps.org/schemas/sitemap/0.9 without changing loc URLs.

Public GitHub API inspection confirmed remote main at 1e5830c5d7144fb16b20d96e3dda6d9f7e0d5f9e and successful latest-commit checks for BOTH Workers Builds: lehi-utah-tree-service and Cloudflare Pages. No GitHub Actions/Wrangler config exists in the current remote tree. Custom-domain binding, current build/deploy commands, root and asset directories are not authenticated/verified. Live /config/config-lehi-tree-pros.json and /scripts/generate_site.py are publicly reachable; do not push authoring/sample configs through a repository-root upload. Confirm assets-only deployment settings before requesting approval for execution. Treat pushes as potentially triggering both integrations. No commit, push, local publish script, deployment, GHL edit or other-site regeneration was performed in preparation.

Production browser checks use tests/browser_media.py --production. The default mode remains preview checks. Source samples/fixtures belong in authoring storage, never the public runtime artifact. Obtain explicit owner approval for the exact reviewed deployment action after resolving/accepting documented discrepancies; preparation is not deployment authorization.


## Local generator corrections (October 21, 2026)

Lehi's 13 legacy phone literals in named content now use `{{PHONE_DISPLAY}}`; authoritative `business.phoneDisplay`, `business.phoneTel`, and GHL form values are unchanged. Owner verified `(385) 217-5381` as the current primary number. The legacy default files are historical inputs only. Both build modes now require a slug. All other sites remain on the default HTML public URL style and were not regenerated.

Use `python3 scripts/preview_site.py lehi-tree-pros --port 8000` for localhost preview with clean route resolution. Plain `http.server` does not resolve extensionless paths to the retained `.html` files. This local server does not implement production redirects or verify Cloudflare routing.

Current correction report: `docs/lehi-media-review/generator-corrections.md`. Earlier frozen deployment archives/manifests are stale and must not be deployed. Only `output/` reflects the current production regeneration. Deployment settings/source exposure and GHL end-to-end behavior still require verification; production approval remains mandatory.


## Local release branch preparation (October 21, 2026)

`release/lehi-image-seo` is a local-only release branch. Lehi reviews are now disabled and example review text is absent from its config; preview-mode regression examples are test fixtures only. Reusable sample-mode rendering remains supported for explicitly configured local demos. Current production output must be generated, not copied from stale root HTML or earlier `.deployment` archives. The Cloudflare Pages command is `python3 scripts/generate_site.py lehi-tree-pros`, repository root working directory, public output `output`. No push, deployment or Cloudflare setting change has been authorized.

The release includes 33 optimized derivatives: **30 WebP plus 3 JPEG social images**, not 33 WebP. Image manifest/license records are tracked; six large originals stay local and are excluded from this release. To reoptimize in a fresh checkout, restore originals from local storage or their recorded licensed source URLs and verify manifest SHA256 hashes. Normal builds require no originals, Pillow or external services. Optional Pillow and browser test requirements are separate files. Other-site untracked files are deliberately not part of this Lehi release.

See `docs/lehi-release.md` for the scoped file list, clean-checkout verification and outstanding production risks. Historical notes above describe earlier snapshots and are superseded by this release note where they differ.
