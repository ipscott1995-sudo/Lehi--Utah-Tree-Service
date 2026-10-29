"""Release inventory must match licensed derivatives and public assets exactly."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseArtifactTests(unittest.TestCase):
    def test_build_contains_only_expected_public_files(self):
        config = json.loads((ROOT / 'config/config-lehi-tree-pros.json').read_text())
        manifest = json.loads((ROOT / config['images']['manifest']).read_text())
        variants = {v['path'] for image in manifest['images'].values()
                    for group in [image, *image.get('renditions', {}).values()]
                    for v in group['variants']}
        self.assertEqual(len(variants), 33)
        self.assertEqual(sum(p.endswith('.webp') for p in variants), 30)
        self.assertEqual(sum(p.endswith('.jpg') for p in variants), 3)
        for path in variants:
            self.assertTrue((ROOT / path).is_file(), path)
        expected = variants | {'index.html', 'about.html', 'contact.html', 'faq.html',
                               'css/styles.css', 'js/main.js', 'robots.txt', 'sitemap.xml'}
        expected |= {s['url'] for s in config['services']}
        expected |= {p['url'] for p in config['locationPages']}
        expected |= set(config.get('deployment', {}).get('publicAssets', []))
        actual = {p.relative_to(ROOT / 'output').as_posix()
                  for p in (ROOT / 'output').rglob('*') if p.is_file()}
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 49 + len(config.get('deployment', {}).get('publicAssets', [])))
        self.assertTrue((ROOT / 'assets/images/lehi-tree-pros/licenses/README.md').is_file())
