# Public deployment security and validation

Implemented locally October 21, 2026. No push, deployment, Cloudflare/DNS change or other-site generation was performed. This extends the existing generator, production validator and publisher; it adds no framework, subscription, API credentials or Python dependencies.

## Before deploying

Run from repository root for one explicit site slug:

```sh
python3 scripts/generate_site.py lehi-tree-pros
python3 scripts/validate_production.py lehi-tree-pros
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The generator now copies only declared public assets and enforces the public-file security policy before reporting success. Validation returns JSON with `result: PASS` or `FAIL`, `ready`, issue codes/severities and exit status 0 or 1. The normal validator is offline. Warnings do not fail a build; errors do. Failed local preflight skips all requested live checks.

The expected artifact consists of configured root-level HTML pages, robots.txt, sitemap.xml, css/styles.css, js/main.js and derivatives referenced by the active image manifest. Unlisted files, private/internal directories (even empty), dotfiles, symlinks, unsupported file types, missing expected files and common credential signatures in text assets fail validation. Explicit additional assets are supported through per-site data:

```json
"deployment": {
  "liveHosts": ["lehitreepros.com", "www.lehitreepros.com"],
  "publicAssets": ["images/favicon.ico"]
}
```

Only add `publicAssets` entries whose source files actually exist and are intended to be public. Allowed types are CSS, browser JavaScript, images, fonts and web manifests. Entries cannot override private-path/type restrictions. Arbitrary JSON, Python, Markdown, environment files, credentials, templates, originals and authoring directories cannot be allowlisted. New output types or generated pages require a reviewed policy/generator change. Generation and preflight use the same policy module (`scripts/deployment_security.py`).

Legacy wholesale copying of css/js/images is replaced with explicit asset copying. If an existing or future site needs an additional browser asset, declare it in that site's `deployment.publicAssets`, then test it. Lehi's current 49 public files remain byte-identical to its tested release. Other sites' data/output were not changed.

The generator's built-in gate validates artifact security in both build modes; it does not turn preview output into production output. The full production validator also rejects preview indexing directives, sample testimonials, unresolved placeholders and unintended review/rating schema while preserving page, canonical, phone, GHL link, sitemap/robots and image checks. Sharing metadata is required when images are enabled; an intentionally media-disabled site is not required to have sharing-image tags.

## Cloudflare Pages workflow

Always publish **output**, with repository root as the working directory. Never serve the authoring repository or its stale root HTML. Existing generator-only build commands gain the automatic artifact-security gate once these local source changes are approved and pushed. For the full production preflight as an enforced build step, the proposed Pages command is:

```sh
python3 scripts/generate_site.py lehi-tree-pros && python3 scripts/validate_production.py lehi-tree-pros
```

Use the matching slug per project; no wildcard or batch publishing. Python 3.9+ and the standard library are sufficient. Pillow and Playwright remain optional local test tools. Changing the remote build command or pushing these files requires explicit approval; no settings were changed by this implementation. Do not run live verification inside a pre-deployment build: the domain will normally still serve the preceding release.

## After an approved deployment

Generate/retain the exact reviewed local build, then run:

```sh
python3 scripts/validate_production.py lehi-tree-pros --live
```

For an optional sanitized report, add `--json /tmp/lehi-production-validation.json`. The parent directory must exist; reports inside the public output directory are prohibited. Do not publish reports or add them to public assets.

`deployment.liveHosts` explicitly selects public hostnames. Without it, only `business.domain` is checked. `--include-www` includes both apex and www for a one-time check without editing site data. Only the site's canonical apex/www pair is permitted; arbitrary origins, credentials in URLs, alternate ports, HTTP redirects and redirects to unrelated hosts are rejected. Lehi's named config now explicitly includes apex and www. Other configs remain unchanged. Each host is checked independently, so a safe apex does not hide an unsafe www or vice versa.

The live phase uses HTTPS GET requests with a read-only user agent, no submitted forms, no calls and no infrastructure APIs. It probes each private path both verbatim and with a unique cache-busting query. A request `no-cache` header is also sent; it is not assumed to force a CDN cache bypass. It never purges caches or modifies WAF rules.

Representative probes include generator/publisher/media scripts, named config/content/image manifests, legacy config, homepage template, AGENTS.md, architecture notes, variables.md, dependency requirements, .git/HEAD and .env. There are 14 paths and 28 probes per host. Private response bodies are examined in memory and never written or included in reports. Reports contain only paths, HTTP status, PASS/FAIL classifications and selected non-cookie/cache headers. Errors and credential matches omit sensitive values.

Classification is body- and content-type-aware:

| Response | Result |
| --- | --- |
| Python/config/template/internal document/Git/environment/credential signatures, including under 403 or 404 | FAIL: source exposure |
| 403 with no source evidence and a suitable error content type | PASS: blocked |
| 404/410 with no source evidence and a suitable error content type | PASS: not found |
| HTTP 200 HTML matching the host homepage title and configured canonical, with no source evidence | PASS: safe homepage fallback |
| Unknown HTML, unexpected successful JSON/binary, transport error, disallowed redirect, oversized/truncated response or server failure | FAIL: unexpected/inconclusive; never silently accepted |

A homepage fallback with HTTP 200 is not a genuine 404. The generator currently does not emit the existing 404 template; adding that public page is a separate reviewed change. WAF rules do **not** need to be identical between sites/hosts. A safe block, genuine not-found response or verified homepage fallback can each pass.

The same live invocation fetches all expected public files from each host and reuses the existing production page/SEO/contact audit. It checks page availability, final public paths, canonical tags, phone display/tel links, exact configured GHL form links, indexing headers/meta, sample/schema exclusion, asset attributes/existence, sharing metadata, sitemap and robots. Non-HTML assets are compared byte-for-byte to local reviewed output. Public downloads exist only in an automatically deleted temporary directory. Known Cloudflare analytics and email-obfuscation script additions are reported as warnings rather than false missing-asset failures; arbitrary third-party additions still fail. The checker does not fetch third-party scripts or submit the external GHL form.

## Local static staging

`scripts/publish_site.py` no longer copies files into the authoring root. It requires a slug and an explicit, separate public-only destination:

```sh
python3 scripts/publish_site.py lehi-tree-pros --destination /tmp/lehi-public-stage
```

This stages files locally only; it never commits, pushes or deploys. The source must pass production validation. The destination must be new or already contain an exact safe public inventory; the tool refuses repository roots, output itself, overlapping directories, symlink destinations, .git/config/source directories and unknown files. It does not erase unknown destination content. No staging command was run against production or another site's checkout.

## Tests and practical limits

`tests/test_deployment_security.py` uses temporary artifacts and inline synthetic response fixtures. It covers private/unlisted/credential files, symlinks and path traversal, allowlisted extra assets, source-copy isolation, safe staging, source exposure under misleading HTTP statuses, WAF blocks, real not-found/error responses, HTML fallbacks, host selection, queries, bounded reads, redirects, network failure, asset drift, hosting-added scripts, CLI reporting and contact regressions. No automated test contacts a live domain. Install the existing optional Pillow requirements to run the two real-encoder tests without skips.

These are fail-closed checks for representative paths and known source/credential patterns, not an exhaustive secret scanner or proof about every URL, cache variant, region or account-side setting. Check rules/routes/custom-domain bindings separately before approving production writes. Explicit extra public assets still require human review. Non-HTML transformations such as CDN minification/image rewriting can trigger asset-drift failures and require investigation; HTML is checked semantically to accommodate known hosting additions. Live HTTP checks do not replace responsive browser checks or prove GHL forwarding/submission/CRM behavior. The existing contact-page two-H1 warning remains.

Lehi's manually deployed WAF protection remains untouched. The code does not create or require a specific WAF rule. No other site's protection is inferred from Lehi's result.

## Activation

1. Review the local change set, then explicitly approve a scoped commit/push including both new support modules, tests and documentation. There is no automatic commit or push in these tools.
2. Confirm each Pages project serves only output. After approval, use the full build command above if all production checks should gate Cloudflare builds; the artifact-security gate already runs within generation.
3. Configure `deployment.liveHosts` for the hostnames actually used by each site (or use `--include-www`). Review any necessary additional browser assets. Apply/verify each site separately; do not bulk-regenerate excluded sites.
4. After each approved deployment completes, run the matching `--live` command. Any FAIL requires investigation, not an automatic repair, purge, re-push or deployment.

## Local implementation verification

All 44 automated tests passed, including the real optional image encoders and complete fixture-driven offline/live CLI workflows. Lehi production preflight passed with only the existing contact-page two-H1 warning. All 49 regenerated public files were byte-for-byte identical to the tested release. `git diff --check` passed.

Changed/new files for this implementation:

- `scripts/deployment_security.py`
- `scripts/live_validation.py`
- `scripts/generate_site.py`
- `scripts/validate_production.py`
- `scripts/publish_site.py`
- `config/config-lehi-tree-pros.json` (explicit apex/www host selection only)
- `tests/test_deployment_security.py`
- `tests/test_site_media.py` (updated asset-copy function contract)
- `docs/deployment-security.md`
- `docs/image-reviews.md`
- `AGENTS.md`

Existing unrelated untracked configurations, originals, historic reports and backup scripts were preserved and are outside this change set. No other site's config/content or generated output was changed.

The new opt-in live command was also exercised read-only against Lehi's configured apex/www hosts: **PASS, exit 0**, with **56 private-path probes and 98 public-file requests**, no private/public failures and no errors. Both WAF-blocked responses and safe homepage fallbacks were observed. Only existing contact H1 and recognized Cloudflare hosting-script warnings remained. No private bodies/report files were saved; no calls, form submissions, infrastructure writes, pushes or deployments occurred.
