# Changelog

## 2026-06-30

### Decisions Locked

- One universal local service template.
- Static HTML/CSS/JS only.
- No frameworks for V1.
- Primary conversion goal is phone calls.
- Secondary conversion goal is quote form submissions.
- External form URLs are used instead of embedded forms.
- Mobile sticky CTA required.
- Large phone number required in hero.
- Reviews added only when real.
- Images planned for V2.
- Human-editable AI copy required.
- Focus is rank-and-rent local lead generation.

### Generator

- Created generate_site.py.
- Generator reads config.json and content.json.
- Generator outputs static site into output/.
- Generator creates sitemap.xml.
- Generator creates robots.txt.
- Generator copies css/js/images assets.
- Generator creates service pages from one template.
- Generator creates location pages from one template.

### Config

- Simplified required inputs.
- Removed unnecessary complexity.
- Added region back as optional but useful for SEO.
- Reserved image fields for V2.

### Content

- Separated factual config from AI-generated content.
- Added content.json workflow.