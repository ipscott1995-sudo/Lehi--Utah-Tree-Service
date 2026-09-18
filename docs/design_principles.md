# Design Principles

## 1. Conversion First

Every page should make it obvious how to call or request a quote.

The user should never need to search for the phone number.

## 2. Mobile First

Most local service visitors are on mobile.

Mobile layouts must prioritize:

- tap-to-call
- quote form button
- fast loading
- readable text
- sticky CTA

## 3. Fast by Default

Generated sites should load quickly.

Use:

- static HTML
- simple CSS
- minimal JS
- no heavy frameworks
- optimized images later

## 4. Honest Trust Signals

Use real trust signals only.

Allowed:

- Free estimates
- Fast response
- Local service
- Residential help
- Licensed/insured only if true

Not allowed unless verified:

- star ratings
- testimonials
- years in business
- awards
- founders
- certifications
- physical address

## 5. Easy to Edit

Generated copy should be human-editable.

The user should be able to improve content manually if a site underperforms.

## 6. Reusable Across Niches

Templates should work for:

- tree service
- concrete
- drywall
- remodeling
- roofing
- plumbing
- HVAC
- junk removal
- other local services

Avoid hardcoding industry-specific assumptions into templates.

## 7. SEO Without Bloat

Pages should be useful, structured, and internally linked.

Do not add content just to hit word count.

Every section should support either:

- ranking
- conversion
- trust
- navigation

## 8. Build for Scale

Every improvement should make future sites better.

Avoid one-off fixes unless absolutely necessary.

## 9. No Architectural Drift

Before changing architecture, check:

- PROJECT_SPEC.md
- ARCHITECTURE.md
- ROADMAP.md

If a new idea is not V1, document it in ROADMAP.md instead of implementing immediately.

## 10. Output Is What Matters

Google and users only see the final static website in output/.

The generator and templates can be complex internally, but the deployed site should be simple, fast, and clean.