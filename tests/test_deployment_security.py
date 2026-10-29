"""Security gates use temporary artifacts and synthetic HTTP fixtures, never production."""
import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import generate_site
import publish_site
import validate_production
from deployment_security import expected_public_files, inspect_output, public_path, safe_detail
from live_validation import Response, SafeRedirect, classify_private, configured_hosts, http_reader, verify_live


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'config/config-lehi-tree-pros.json').read_text())
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / 'output'
        shutil.copytree(ROOT / 'output', self.output)
        self.home = (self.output / 'index.html').read_bytes()
        self.home_response = Response(200, {'Content-Type': 'text/html'}, self.home, 'https://lehitreepros.com/')

    def classify(self, path, body, status=200, content_type='text/plain'):
        return classify_private(path, Response(status, {'Content-Type': content_type}, body, 'https://lehitreepros.com' + path), self.home_response, 'https://lehitreepros.com/')

    def fake_fetch(self, url, max_bytes=2 * 1024 * 1024):
        parsed = urlsplit(url)
        path = parsed.path
        from site_urls import SiteURLs
        filename = SiteURLs(self.config).physical(path)
        file = self.output / filename
        if file.is_file():
            suffix = file.suffix
            kind = 'text/html' if suffix == '.html' else 'application/octet-stream'
            return Response(200, {'Content-Type': kind}, file.read_bytes(), url)
        # Safe SPA fallback on one host, no mandatory uniform WAF policy.
        if parsed.hostname.startswith('www.'):
            return Response(200, {'Content-Type': 'text/html'}, self.home, url)
        return Response(403, {'Content-Type': 'text/html'}, b'<html><title>Blocked</title>Forbidden</html>', url)

    def test_exact_inventory_and_missing_files(self):
        self.assertEqual(inspect_output(self.config, self.output, ROOT), [])
        self.assertEqual(len(expected_public_files(self.config, ROOT)), 49 + len(self.config['deployment'].get('publicAssets', [])))
        (self.output / 'js/main.js').unlink()
        self.assertIn('missing-public-file', {i['code'] for i in inspect_output(self.config, self.output, ROOT)})

    def test_private_unexpected_and_credential_files_are_rejected(self):
        for name in ['scripts/leak.py', 'config/config-test.json', 'templates/home.html', '.env', '.git/HEAD', 'images/unused.webp', 'js/unlisted.js']:
            path = self.output / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('synthetic internal file')
        result = validate_production.audit(self.config, self.output)
        self.assertFalse(result['ready'])
        self.assertTrue({'private-output-path', 'unexpected-public-file'} <= {i['code'] for i in result['issues']})
        self.assertNotIn('synthetic internal file', json.dumps(result))

    def test_credentials_inside_allowed_html_fail_without_disclosure(self):
        # Synthetic canary, not a real credential.
        canary = 'fixture-secret-never-print-4281'
        path = self.output / 'index.html'
        path.write_text(path.read_text() + '\n<script>const api_key = "' + canary + '";</script>')
        result = validate_production.audit(self.config, self.output)
        self.assertFalse(result['ready'])
        self.assertIn('credential-in-output', {i['code'] for i in result['issues']})
        self.assertNotIn(canary, json.dumps(result))

    def test_sensitive_urls_and_unknown_directories_are_not_silently_accepted(self):
        for value in ['https://fixture-user:fixture-password@example.com/', 'https://example.com/?auth=fixture-secret', 'https://example.com/?api_key=fixture-secret']:
            self.assertEqual(safe_detail(value), '[sensitive value omitted]')
        (self.output / 'internal-empty-folder').mkdir()
        self.assertIn('unexpected-public-directory', {i['code'] for i in inspect_output(self.config, self.output, ROOT)})

    def test_symlinks_and_empty_internal_directories_fail(self):
        (self.output / 'private-link').symlink_to(ROOT / 'config')
        (self.output / 'config').mkdir()
        codes = {i['code'] for i in inspect_output(self.config, self.output, ROOT)}
        self.assertTrue({'output-symlink', 'private-output-path'} <= codes)

    def test_additional_assets_require_explicit_safe_configuration(self):
        config = copy.deepcopy(self.config)
        config['deployment'].setdefault('publicAssets', []).append('images/favicon.ico')
        (self.output / 'images/favicon.ico').write_bytes(b'fixture-icon')
        self.assertEqual(inspect_output(config, self.output, ROOT), [])
        for name in ['config/example.js', 'Config/example.js', '../outside.css', '/absolute.css', 'images/.secret.css', 'images/secret.json', 'AGENTS.md', 'scripts/x.html', 'images/%2e%2e/config.css']:
            with self.assertRaises(ValueError):
                public_path(name)

    def test_generator_rejects_unsafe_page_paths_before_removing_output(self):
        config = copy.deepcopy(self.config)
        config['services'][0]['url'] = '../escape.html'
        original = generate_site.load_json
        def load(path):
            return config if path.name == 'config-lehi-tree-pros.json' else original(path)
        marker = self.output / 'keep.txt'
        marker.write_text('preserved')
        with patch.object(generate_site, 'OUTPUT_DIR', self.output), patch.object(generate_site, 'load_json', side_effect=load), patch.object(sys, 'argv', ['generate_site.py', 'lehi-tree-pros']):
            with self.assertRaises(ValueError):
                generate_site.main()
        self.assertEqual(marker.read_text(), 'preserved')

    def test_generation_copies_only_allowlisted_assets(self):
        config = copy.deepcopy(self.config)
        config['images'] = {'useImages': False}
        from site_media import SiteImages
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder).resolve()
            (source / 'css').mkdir(); (source / 'js').mkdir()
            (source / 'css/styles.css').write_text('body{}')
            (source / 'js/main.js').write_text('void 0;')
            (source / 'js/private-config.json').write_text('{"internal": true}')
            for name in config['deployment'].get('publicAssets', []):
                target = source / name; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_bytes())
            with patch.object(generate_site, 'ROOT', source), patch.object(generate_site, 'OUTPUT_DIR', source / 'output'):
                generate_site.copy_assets(SiteImages(source, config), config)
            self.assertFalse((source / 'output/js/private-config.json').exists())
            self.assertTrue((source / 'output/js/main.js').is_file())

    def test_media_disabled_site_has_a_valid_minimal_public_build(self):
        config = copy.deepcopy(self.config)
        config['images'] = {'useImages': False}
        config.pop('deployment')
        original = generate_site.load_json
        def load(path):
            return config if path.name == 'config-lehi-tree-pros.json' else original(path)
        with patch.object(generate_site, 'OUTPUT_DIR', self.output), patch.object(generate_site, 'load_json', side_effect=load), patch.object(sys, 'argv', ['generate_site.py', 'lehi-tree-pros']), contextlib.redirect_stdout(io.StringIO()):
            generate_site.main()
        result = validate_production.audit(config, self.output)
        self.assertTrue(result['ready'], result['issues'])
        self.assertEqual(result['counts'], {'pages': 12, 'images': 0, 'socialImages': 0})
        self.assertEqual(len(expected_public_files(config, ROOT)), 16)

    def test_blocked_not_found_and_safe_fallback_fixtures_pass(self):
        for status in (403, 404, 410):
            self.assertEqual(self.classify('/scripts/generate_site.py', b'<html><title>Unavailable</title></html>', status, 'text/html')[0], 'PASS')
        self.assertEqual(self.classify('/config/config-test.json', b'{"error":"Not found"}', 404, 'application/json')[0], 'PASS')
        self.assertEqual(self.classify('/AGENTS.md', self.home, 200, 'text/html'), ('PASS', 'safe-homepage-fallback'))

    def test_exposure_is_detected_regardless_of_status_or_type(self):
        examples = [('/scripts/generate_site.py', b'import json\ndef main():\n    pass'),
                    ('/config/config-test.json', b'{"business":{"name":"Fixture business"}}'),
                    ('/AGENTS.md', b'# Project instructions\nInternal authoring rules'),
                    ('/templates/home.html', b'<html>{{BUSINESS_NAME}}</html>'),
                    ('/.git/HEAD', b'ref: refs/heads/main\n'),
                    ('/.env', b'FIXTURE_SETTING=private-value\n')]
        for path, body in examples:
            for status in (200, 403, 404):
                with self.subTest(path=path, status=status):
                    self.assertTrue(self.classify(path, body, status, 'text/html')[1].startswith('source-exposed:'))

    def test_unknown_html_binary_errors_and_truncation_fail_closed(self):
        self.assertEqual(self.classify('/AGENTS.md', b'<html><title>Unknown</title></html>', 200, 'text/html')[0], 'FAIL')
        self.assertEqual(self.classify('/config/x.json', b'unknown binary', 200, 'application/octet-stream')[0], 'FAIL')
        self.assertEqual(self.classify('/config/x.json', b'<html>Server error</html>', 500, 'text/html')[0], 'FAIL')
        r = Response(403, {'Content-Type': 'text/html'}, b'<html>Blocked', '', truncated=True)
        self.assertEqual(classify_private('/AGENTS.md', r, self.home_response, 'https://lehitreepros.com/')[0], 'FAIL')

    def test_live_hosts_are_explicit_and_restricted(self):
        self.assertEqual(configured_hosts(self.config), ['lehitreepros.com', 'www.lehitreepros.com'])
        config = copy.deepcopy(self.config); config.pop('deployment')
        self.assertEqual(configured_hosts(config), ['lehitreepros.com'])
        self.assertEqual(configured_hosts(config, True), ['lehitreepros.com', 'www.lehitreepros.com'])
        for host in ['https://example.com', 'unrelated.example', 'lehitreepros.com:8443', 'user:secret@lehitreepros.com']:
            config['deployment'] = {'liveHosts': [host]}
            with self.assertRaises(ValueError):
                configured_hosts(config)

    def test_transport_rejects_unsafe_requests_and_redirects(self):
        reader = http_reader(['lehitreepros.com'])
        for url in ['http://lehitreepros.com/', 'https://elsewhere.example/', 'https://user:secret@lehitreepros.com/']:
            self.assertEqual(reader(url).error, 'unsafe-request-url')
        handler = SafeRedirect(['lehitreepros.com'])
        import urllib.error
        for url in ['http://lehitreepros.com/', 'https://outside.example/?token=secret']:
            with self.assertRaises(urllib.error.URLError):
                handler.redirect_request(None, None, 302, '', {}, url)

    def test_full_live_workflow_accepts_different_protections_and_checks_query_variants(self):
        calls = []
        def fetch(url, max_bytes=2 * 1024 * 1024):
            calls.append(url)
            return self.fake_fetch(url, max_bytes)
        result = verify_live(self.config, 'lehi-tree-pros', ROOT, self.output, validate_production.audit, fetch=fetch)
        self.assertTrue(result['ready'], result['issues'])
        self.assertEqual(len(result['publicChecks']), 2 * len(expected_public_files(self.config, ROOT)))
        self.assertTrue(any(p['reason'] == 'blocked' for p in result['privateChecks']))
        self.assertTrue(any(p['reason'] == 'safe-homepage-fallback' for p in result['privateChecks']))
        self.assertTrue(any(p['cacheBusting'] for p in result['privateChecks']))
        self.assertTrue(all(url.startswith(('https://lehitreepros.com/', 'https://www.lehitreepros.com/')) for url in calls))

    def test_live_workflow_exposure_and_contact_regression_fail_without_body_in_report(self):
        canary = 'fixture-do-not-report-5984'
        def fetch(url, max_bytes=2 * 1024 * 1024):
            if urlsplit(url).path == '/config/config-lehi-tree-pros.json':
                return Response(200, {'Content-Type': 'application/json'}, json.dumps({'business': {'internal': canary}}).encode(), url)
            response = self.fake_fetch(url, max_bytes)
            if urlsplit(url).path == '/contact':
                response.body = response.body.replace(self.config['business']['formUrl'].encode(), b'https://example.com/wrong')
            return response
        result = verify_live(self.config, 'lehi-tree-pros', ROOT, self.output, validate_production.audit, fetch=fetch)
        self.assertFalse(result['ready'])
        self.assertIn('missing-form', {i['code'] for i in result['issues']})
        self.assertTrue(any(p['reason'] == 'source-exposed:private-json' for p in result['privateChecks']))
        self.assertNotIn(canary, json.dumps(result))

    def test_known_hosting_scripts_do_not_create_false_live_failures(self):
        def fetch(url, max_bytes=2 * 1024 * 1024):
            response = self.fake_fetch(url, max_bytes)
            if urlsplit(url).path == '/':
                response.body = response.body.replace(b'</body>', b'<script src="https://static.cloudflareinsights.com/beacon.min.js/version" data-cf-beacon=\'{"token":"public-analytics-id"}\'></script><script src="/cdn-cgi/scripts/123abc/cloudflare-static/email-decode.min.js"></script></body>')
            return response
        result = verify_live(self.config, 'lehi-tree-pros', ROOT, self.output, validate_production.audit, fetch=fetch)
        self.assertTrue(result['ready'], result['issues'])
        self.assertIn('hosting-injected-asset', {i['code'] for i in result['issues']})

    def test_live_network_failure_and_asset_drift_fail(self):
        def fetch(url, max_bytes=2 * 1024 * 1024):
            if urlsplit(url).path == '/AGENTS.md':
                return Response(0, {}, b'', '', error='fixture-network-error')
            response = self.fake_fetch(url, max_bytes)
            if urlsplit(url).path == '/css/styles.css':
                response.body += b'/* unexpected live change */'
            return response
        result = verify_live(self.config, 'lehi-tree-pros', ROOT, self.output, validate_production.audit, fetch=fetch)
        self.assertFalse(result['ready'])
        self.assertIn('live-asset-drift', {i['code'] for i in result['issues']})
        self.assertTrue(any(p['reason'] == 'inconclusive-response' for p in result['privateChecks']))

    def test_transport_bounds_reads_and_does_not_return_exception_secrets(self):
        class FakeResponse(io.BytesIO):
            code = 200
            headers = {'Content-Type': 'text/plain'}
            def geturl(self):
                return 'https://lehitreepros.com/AGENTS.md'
        with patch('live_validation.urllib.request.build_opener') as opener:
            opener.return_value.open.return_value = FakeResponse(b'abcdef')
            reader = http_reader(['lehitreepros.com'])
            response = reader('https://lehitreepros.com/AGENTS.md', 3)
            self.assertEqual(response.body, b'abc')
            self.assertTrue(response.truncated)
            opener.return_value.open.side_effect = RuntimeError('password=fixture-never-report')
            response = reader('https://lehitreepros.com/AGENTS.md')
            self.assertEqual(response.error, 'request-failed:RuntimeError')

    def test_cli_has_no_network_by_default_and_skips_live_on_unsafe_output(self):
        with patch('live_validation.verify_live') as live, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(validate_production.main(['lehi-tree-pros', '--output-dir', str(self.output)]), 0)
            live.assert_not_called()
            (self.output / 'leak.py').write_text('import json')
            self.assertEqual(validate_production.main(['lehi-tree-pros', '--output-dir', str(self.output), '--live']), 1)
            live.assert_not_called()
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            validate_production.main(['lehi-tree-pros', '--output-dir', str(self.output), '--json', str(self.output / 'internal.json')])

    def test_live_cli_reuses_existing_audit_and_emits_pass_without_source_bodies(self):
        with patch('live_validation.http_reader', return_value=self.fake_fetch), contextlib.redirect_stdout(io.StringIO()) as stream:
            code = validate_production.main(['lehi-tree-pros', '--output-dir', str(self.output), '--live'])
        report = json.loads(stream.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(report['result'], 'PASS')
        self.assertEqual(report['live']['result'], 'PASS')
        self.assertEqual(len(report['live']['privateChecks']), 56)
        self.assertEqual(len(report['live']['publicChecks']), 2 * len(expected_public_files(self.config, ROOT)))
        self.assertNotIn('body', stream.getvalue())

    def test_unreachable_host_fails_without_repeating_every_request(self):
        calls = []
        def fetch(url, max_bytes=2 * 1024 * 1024):
            calls.append(url)
            return Response(0, {}, b'', '', error='fixture-timeout')
        result = verify_live(self.config, 'lehi-tree-pros', ROOT, self.output, validate_production.audit, fetch=fetch)
        self.assertFalse(result['ready'])
        self.assertEqual(len(calls), 2)
        self.assertEqual({i['code'] for i in result['issues']}, {'live-host-unavailable'})

    def test_publisher_refuses_authoring_roots_and_unsafe_existing_destinations(self):
        with self.assertRaises(ValueError):
            publish_site.stage(self.config, self.output, ROOT)
        target = Path(self.temp.name) / 'repo'
        target.mkdir(); (target / '.git').mkdir()
        with self.assertRaises(ValueError):
            publish_site.stage(self.config, self.output, target)
        target2 = Path(self.temp.name) / 'public'
        with contextlib.redirect_stdout(io.StringIO()):
            publish_site.stage(self.config, self.output, target2)
        self.assertEqual(inspect_output(self.config, target2, ROOT), [])
