"""Reusable route and authoritative contact regression checks."""
import copy
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import generate_site
from site_urls import SiteURLs
from validate_production import audit


class URLTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'config/config-lehi-tree-pros.json').read_text())

    def test_release_configuration_contains_no_sample_reviews(self):
        self.assertEqual(self.config.get('reviews'), {'mode': 'disabled'})

    def test_explicit_slug_required_without_touching_output(self):
        for args in ([], ['--preview']):
            with tempfile.TemporaryDirectory() as folder:
                target = Path(folder)
                marker = target / 'keep.txt'
                marker.write_text('untouched')
                with patch.object(generate_site, 'OUTPUT_DIR', target), patch.object(sys, 'argv', ['generate_site.py', *args]), contextlib.redirect_stderr(io.StringIO()) as error:
                    with self.assertRaises(SystemExit) as caught:
                        generate_site.main()
                self.assertEqual(caught.exception.code, 2)
                self.assertIn('explicit site slug', error.getvalue())
                self.assertEqual(marker.read_text(), 'untouched')

    def test_url_styles_are_opt_in_and_preserve_external_assets_and_suffixes(self):
        routes = SiteURLs(self.config)
        self.assertEqual(routes.absolute('index.html'), 'https://lehitreepros.com/')
        self.assertEqual(routes.absolute('tree-removal.html'), 'https://lehitreepros.com/tree-removal')
        markup = '<a href="about.html?ref=nav#team">About</a><a href="https://elsewhere.example/about.html">Other</a><img src="images/about.html"><script>{"url":"https://lehitreepros.com/contact.html"}</script>'
        result = routes.rewrite(markup)
        self.assertIn('href="/about?ref=nav#team"', result)
        self.assertIn('https://elsewhere.example/about.html', result)
        self.assertIn('images/about.html', result)
        self.assertIn('"url":"https://lehitreepros.com/contact"', result)
        legacy = copy.deepcopy(self.config)
        legacy.pop('publicUrlStyle')
        self.assertEqual(SiteURLs(legacy).rewrite(markup), markup)
        self.assertEqual(SiteURLs(legacy).absolute('about.html'), 'https://lehitreepros.com/about.html')
        legacy['publicUrlStyle'] = 'invalid'
        with self.assertRaises(ValueError):
            SiteURLs(legacy)

    def test_config_contacts_drive_all_copy_and_production_routes(self):
        config = copy.deepcopy(self.config)
        config['business']['phoneDisplay'] = '(801) 555-0101'
        config['business']['phoneTel'] = '+18015550101'
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'site'
            original = generate_site.load_json
            def load(path):
                return config if path.name == 'config-lehi-tree-pros.json' else original(path)
            with patch.object(generate_site, 'OUTPUT_DIR', target), patch.object(generate_site, 'load_json', side_effect=load), patch.object(sys, 'argv', ['generate_site.py', 'lehi-tree-pros']):
                generate_site.main()
            result = audit(config, target)
            self.assertTrue(result['ready'], result['issues'])
            for page in target.glob('*.html'):
                html = page.read_text()
                self.assertNotIn('(385) 534-4337', html)
                self.assertNotIn('(385) 217-5381', html)
                self.assertIn(config['business']['phoneDisplay'], html)
                self.assertIn(config['business']['formUrl'], html)
                self.assertNotIn('tally.so', html)
                self.assertNotIn('SAMPLE —', html)
                self.assertNotIn('noindex', html)
