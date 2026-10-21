"""Ensure production validation cannot silently approve preview or conflicting data."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_production import audit


class ProductionPreflightTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'config/config-lehi-tree-pros.json').read_text())
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / 'site'
        shutil.copytree(ROOT / 'output', self.output)

    def test_production_build_passes(self):
        result = audit(self.config, self.output)
        self.assertTrue(result['ready'], result['issues'])
        self.assertEqual(result['counts'], {'pages': 12, 'images': 11, 'socialImages': 12})

    def test_preview_and_review_schema_are_rejected(self):
        path = self.output / 'index.html'
        path.write_text(path.read_text().replace('</head>', '<meta name="robots" content="noindex, nofollow"><script type="application/ld+json">{"@type":"Review"}</script></head>').replace('</main>', '<p>Example homeowner (fictional)</p></main>'))
        result = audit(self.config, self.output)
        codes = {issue['code'] for issue in result['issues']}
        self.assertFalse(result['ready'])
        self.assertTrue({'preview-content', 'indexing-block', 'review-schema'} <= codes)

    def test_phone_conflict_and_missing_canonical_are_rejected(self):
        path = self.output / 'index.html'
        html = path.read_text().replace(self.config['business']['phoneDisplay'], '(385) 534-4337')
        html = html.replace('<link rel="canonical" href="https://lehitreepros.com/">', '')
        path.write_text(html)
        result = audit(self.config, self.output)
        self.assertFalse(result['ready'])
        codes = {issue['code'] for issue in result['issues']}
        self.assertTrue({'conflicting-phone-copy', 'canonical-count'} <= codes)

    def test_legacy_canonicals_links_sitemap_and_changed_form_are_rejected(self):
        path = self.output / 'contact.html'
        html = path.read_text().replace('https://lehitreepros.com/contact"', 'https://lehitreepros.com/contact.html"')
        html = html.replace('href="/about"', 'href="about.html"')
        html = html.replace(self.config['business']['formUrl'], 'https://api.leadconnectorhq.com/widget/form/wrong')
        path.write_text(html)
        sitemap = self.output / 'sitemap.xml'
        sitemap.write_text(sitemap.read_text().replace('https://lehitreepros.com/about<', 'https://lehitreepros.com/about.html<'))
        result = audit(self.config, self.output)
        self.assertFalse(result['ready'])
        codes = {issue['code'] for issue in result['issues']}
        self.assertTrue({'canonical-mismatch', 'internal-url-style', 'form-link-mismatch', 'sitemap-coverage'} <= codes)
