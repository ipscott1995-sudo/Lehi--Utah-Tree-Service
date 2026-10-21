"""Regression checks for the optional media contract and local Lehi build."""
import copy
import json
import re
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import generate_site
from site_media import SiteImages, homepage_reviews, local_path
from site_urls import SiteURLs


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def attrs(self, tag):
        return [a for t, a in self.elements if t == tag]


class MediaTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'config/config-lehi-tree-pros.json').read_text())
        self.manifest = json.loads((ROOT / self.config['images']['manifest']).read_text())
        # Synthetic content lives only in tests, never in Lehi release configuration.
        self.config['reviews'] = {'mode': 'sample', 'items': [{'text': f'Test-only review layout fixture {i}.'} for i in range(1, 4)]}

    def test_sample_reviews_require_preview_and_are_obvious(self):
        self.assertEqual(homepage_reviews(self.config), '')
        html = homepage_reviews(self.config, True)
        self.assertEqual(html.count('SAMPLE — demonstration only'), 3)
        self.assertEqual(html.count('(fictional)'), 3)
        self.assertIn('not customer testimonials or Google reviews', html)
        self.assertNotIn('application/ld+json', html)
        self.assertNotIn('AggregateRating', html)
        self.assertNotIn('testimonial-stars', html)

    def test_review_content_is_escaped_and_google_requires_source(self):
        config = {'reviews': {'mode': 'google', 'items': [{'author': 'Alex <script>', 'text': '<img onerror="x">', 'rating': 5, 'sourceUrl': 'https://www.google.com/maps/reviews/example'}]}}
        html = homepage_reviews(config)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<img', html)
        self.assertIn('Read on Google', html)
        config['reviews']['items'][0]['sourceUrl'] = 'javascript:alert(1)'
        with self.assertRaises(ValueError):
            homepage_reviews(config)
        config['reviews']['items'][0]['sourceUrl'] = 'https://example.com'
        with self.assertRaises(ValueError):
            homepage_reviews(config)

    def test_path_traversal_is_rejected(self):
        for value in ['/etc/passwd', '../outside.webp', 'config/config.json']:
            with self.assertRaises(ValueError):
                local_path(ROOT, value, 'images/optimized')

    def test_optional_images_do_not_copy_other_site_libraries(self):
        disabled = copy.deepcopy(self.config)
        disabled['images'] = {'useImages': False}
        images = SiteImages(ROOT, disabled)
        self.assertEqual(images.figure('index.html', 'hero'), '')
        with tempfile.TemporaryDirectory() as folder, patch.object(generate_site, 'OUTPUT_DIR', Path(folder)):
            generate_site.copy_assets(images, disabled)
            self.assertFalse((Path(folder) / 'images/optimized').exists())
            self.assertTrue((Path(folder) / 'css/styles.css').exists())

    def test_missing_alt_or_asset_fails_before_build(self):
        for mutate in [lambda m: m['images']['removal'].update(alt=''), lambda m: m['images']['removal']['variants'][0].update(path='images/optimized/nonexistent.webp')]:
            manifest = copy.deepcopy(self.manifest)
            mutate(manifest)
            with patch('site_media.json.loads', return_value=manifest):
                with self.assertRaises(ValueError):
                    SiteImages(ROOT, self.config)

    def test_responsive_loading_without_visible_credits(self):
        images = SiteImages(ROOT, self.config)
        hero = images.figure('index.html', 'hero')
        card = images.figure('index.html', 'service:tree-trimming')
        self.assertIn('fetchpriority="high"', hero)
        self.assertIn('loading="eager"', hero)
        self.assertIn('loading="lazy"', card)
        self.assertIn('srcset=', hero)
        self.assertIn('width=', hero)
        self.assertNotIn('figcaption', card)
        self.assertNotIn('not a Lehi Tree Pros project or crew', card)
        self.assertNotIn('Samuel Vogl', card)
        self.assertNotIn('<a ', card)
        self.assertEqual(images.images['trimming']['source']['creator'], 'Samuel Vogl')

    def test_local_lehi_build_has_valid_assets_seo_and_integrations(self):
        expected_pages = {'index.html', 'about.html', 'contact.html', 'faq.html'} | {s['url'] for s in self.config['services']} | {p['url'] for p in self.config['locationPages']}
        self.assertEqual({p.name for p in (ROOT / 'output').glob('*.html')}, expected_pages)
        business = self.config['business']
        seen_images = set()
        for name in expected_pages:
            html = (ROOT / 'output' / name).read_text()
            parsed = Page(html)
            self.assertNotIn('{{', html, name)
            # Existing contact template contains two H1s; preserve and flag this
            # unrelated baseline issue rather than silently changing its copy/layout.
            self.assertEqual(len(parsed.attrs('h1')), 2 if name == 'contact.html' else 1, name)
            self.assertNotIn('AggregateRating', html)
            canonical = next(a['href'] for a in parsed.attrs('link') if a.get('rel') == 'canonical')
            self.assertEqual(canonical, SiteURLs(self.config).absolute(name))
            self.assertTrue(any(a.get('name') == 'description' and a.get('content') for a in parsed.attrs('meta')))
            for data in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
                schema = json.loads(data)
                self.assertNotIn(schema.get('@type'), ['Review', 'AggregateRating'])
            for a in parsed.attrs('a'):
                href = a.get('href', '')
                if href.startswith('tel:'):
                    self.assertEqual(href, 'tel:' + business['phoneTel'])
                if '/widget/form/' in href:
                    self.assertEqual(href, business['formUrl'])
            for tag, a in parsed.elements:
                for field in (['src'] if tag in ['img', 'script'] else ['href'] if tag in ['a', 'link'] else []):
                    value = a.get(field, '')
                    if not value or urlparse(value).scheme or value.startswith('#'):
                        continue
                    self.assertTrue((ROOT / 'output' / SiteURLs(self.config).physical(unquote(urlparse(value).path))).exists(), f'{name}: {value}')
            for image in parsed.attrs('img'):
                self.assertTrue(image.get('alt', '').strip())
                self.assertNotIn('Lehi', image['alt'])
                self.assertGreater(int(image['width']), 0)
                self.assertGreater(int(image['height']), 0)
                for candidate in image['srcset'].split(','):
                    path, width = candidate.strip().split()
                    self.assertTrue((ROOT / 'output' / path).is_file())
                    self.assertRegex(width, r'^\d+w$')
                    seen_images.add(path)
            if name != 'index.html':
                self.assertNotIn('homepage-reviews', html)
        expected_assets = {v['path'] for image in self.manifest['images'].values() for group in [image, *[r for name,r in image.get('renditions', {}).items() if name == 'card']] for v in group['variants']}
        self.assertEqual(seen_images, expected_assets)
        self.assertEqual({p.relative_to(ROOT / 'output').as_posix() for p in (ROOT / 'output/images').rglob('*.webp')}, expected_assets)
        self.assertFalse((ROOT / 'output/assets').exists())
        self.assertEqual((ROOT / 'output/sitemap.xml').read_text().count('<loc>'), 12)
        import xml.etree.ElementTree as ET
        self.assertEqual(ET.parse(ROOT / 'output/sitemap.xml').getroot().tag, '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')

    def test_social_images_use_configured_domain_and_existing_licensed_assets(self):
        images = SiteImages(ROOT, self.config)
        config = copy.deepcopy(self.config)
        config['business']['domain'] = 'future-site.example'
        for page in ['index.html', 'stump-grinding.html', 'tree-trimming.html', 'contact.html']:
            meta = Page(images.social_meta(config, page)).attrs('meta')
            values = {a.get('property', a.get('name')): a['content'] for a in meta}
            self.assertEqual(values['og:image'], values['twitter:image'])
            self.assertTrue(values['og:image'].startswith('https://future-site.example/images/optimized/'))
            self.assertTrue((ROOT / urlparse(values['og:image']).path.lstrip('/')).is_file())
            self.assertEqual(values['og:image:width'], '1200')
            self.assertEqual(values['og:image:height'], '630')
            self.assertEqual(values['og:image:type'], 'image/jpeg')
        disabled = copy.deepcopy(self.config)
        disabled['images']['useImages'] = False
        self.assertEqual(SiteImages(ROOT, disabled).social_meta(disabled, 'index.html'), '')

    def test_card_crop_preserves_alt_and_service_portrait(self):
        images = SiteImages(ROOT, self.config)
        card = Page(images.figure('index.html', 'service:tree-trimming')).attrs('img')[0]
        service = Page(images.figure('tree-trimming.html', 'main')).attrs('img')[0]
        self.assertEqual(card['alt'], service['alt'])
        self.assertIn('-card-', card['src'])
        self.assertNotIn('-card-', service['src'])
        self.assertAlmostEqual(int(card['width']) / int(card['height']), 4 / 3)
        self.assertGreater(int(service['height']), int(service['width']))
        self.assertEqual(card['loading'], 'lazy')
        self.assertEqual(service['loading'], 'lazy')

    def test_standard_build_omits_samples_and_preview_noindex(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'site'
            with patch.object(generate_site, 'OUTPUT_DIR', target), patch.object(sys, 'argv', ['generate_site.py', 'lehi-tree-pros']):
                generate_site.main()
                html = (target / 'index.html').read_text()
                self.assertNotIn('homepage-reviews', html)
                self.assertNotIn('noindex', html)
                self.assertIn('site-image--hero', html)
            original_load = generate_site.load_json
            def preview_load(path):
                return self.config if path.name == 'config-lehi-tree-pros.json' else original_load(path)
            with patch.object(generate_site, 'OUTPUT_DIR', target), patch.object(generate_site, 'load_json', side_effect=preview_load), patch.object(sys, 'argv', ['generate_site.py', 'lehi-tree-pros', '--preview']):
                generate_site.main()
                for path in target.glob('*.html'):
                    self.assertIn('noindex, nofollow', path.read_text())
                self.assertEqual((target / 'index.html').read_text().count('SAMPLE — demonstration only'), 3)


if __name__ == '__main__':
    unittest.main()
