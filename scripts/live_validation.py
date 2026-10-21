"""Opt-in HTTPS GET verification supporting the existing production validator."""
import hashlib
import re
import tempfile
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from deployment_security import expected_public_files, private_paths, safe_detail, source_evidence
from site_urls import SiteURLs


@dataclass
class Response:
    status: int
    headers: dict
    body: bytes
    final_url: str
    error: str = ''
    truncated: bool = False

    def __post_init__(self):
        self.headers = {k.lower(): v for k, v in self.headers.items()}


def configured_hosts(config, include_www=False):
    domain = config['business']['domain']
    base = domain.removeprefix('www.')
    hosts = config.get('deployment', {}).get('liveHosts', [domain])
    if not isinstance(hosts, list) or not hosts:
        raise ValueError('deployment.liveHosts must be a nonempty hostname list')
    hosts = [*hosts, domain]
    if include_www:
        hosts += [base, 'www.' + base]
    for host in hosts:
        if not isinstance(host, str) or host not in {base, 'www.' + base} or not re.fullmatch(r'[a-z0-9]+(?:[.-][a-z0-9]+)*\.[a-z]{2,}', host):
            raise ValueError('Live checks permit only the configured apex/www hostnames')
    return list(dict.fromkeys(hosts))


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, hosts):
        self.hosts = set(hosts)

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        if parsed.scheme != 'https' or parsed.hostname not in self.hosts or parsed.port not in (None, 443) or parsed.username or parsed.password:
            raise urllib.error.URLError('redirect-outside-configured-hosts')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def http_reader(hosts, timeout=15):
    opener = urllib.request.build_opener(SafeRedirect(hosts))

    def read(url, max_bytes=2 * 1024 * 1024):
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.hostname not in hosts or parsed.username or parsed.password or parsed.port not in (None, 443):
            return Response(0, {}, b'', '', 'unsafe-request-url')
        request = urllib.request.Request(url, headers={
            'User-Agent': 'RankRent-ReadOnly-Production-Check/1.0',
            'Cache-Control': 'no-cache', 'Accept-Encoding': 'identity',
        })
        try:
            try:
                response = opener.open(request, timeout=timeout)
            except urllib.error.HTTPError as error:
                response = error
            with response:
                body = response.read(max_bytes + 1)
                return Response(response.code, dict(response.headers), body[:max_bytes], response.geturl(), truncated=len(body) > max_bytes)
        except Exception as error:
            # Exception messages and redirect URLs can contain secrets; omit them.
            return Response(0, {}, b'', '', 'request-failed:' + type(error).__name__)
    return read


class HTMLIdentity(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.canonical = ''
        self.title = ''
        self.in_title = False
        self.html = False
        self.feed(body.decode('utf-8', errors='replace'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.html |= tag == 'html'
        self.in_title |= tag == 'title'
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs.get('href', '')

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def classify_private(path, response, homepage, canonical_home):
    content_type = response.headers.get('content-type', '').split(';')[0].lower()
    evidence = source_evidence(path, response.body, content_type)
    if evidence:
        return 'FAIL', 'source-exposed:' + evidence
    if response.error or response.truncated:
        return 'FAIL', 'inconclusive-response'
    # Never accept a binary/JSON source simply because its status is 403 or 404.
    if response.status in (403, 404, 410) and content_type in ('', 'text/html', 'text/plain', 'application/json', 'application/problem+json'):
        return 'PASS', 'blocked' if response.status == 403 else 'not-found'
    if response.status == 200 and content_type == 'text/html' and homepage.status == 200:
        actual, home = HTMLIdentity(response.body), HTMLIdentity(homepage.body)
        if actual.html and actual.title.strip() and actual.title == home.title and actual.canonical == home.canonical == canonical_home:
            return 'PASS', 'safe-homepage-fallback'
    return 'FAIL', 'unexpected-private-path-response'


def verify_live(config, slug, root, output, audit, include_www=False, fetch=None):
    """Check source bodies and reuse the offline page/SEO audit on fetched public files.

    No private response bodies or sensitive headers are persisted or returned.
    Public downloads exist only in an automatically removed temporary directory.
    """
    hosts = configured_hosts(config, include_www)
    fetch = fetch or http_reader(hosts)
    routes = SiteURLs(config)
    expected = expected_public_files(config, root)
    probes, public, issues = [], [], []
    token = uuid.uuid4().hex
    for host in hosts:
        homepage = fetch('https://' + host + '/')
        if homepage.error or not homepage.status:
            issues.append({'code': 'live-host-unavailable', 'host': host, 'page': '/', 'severity': 'error', 'detail': 'Homepage request failed; remaining requests to this host skipped'})
            public.append({'host': host, 'path': '/', 'httpStatus': homepage.status, 'result': 'FAIL'})
            continue
        for path in private_paths(slug):
            for suffix in ('', '?__rr_verify=' + token):
                response = fetch('https://' + host + path + suffix)
                status, reason = classify_private(path, response, homepage, routes.absolute('index.html'))
                probes.append({'host': host, 'path': path, 'cacheBusting': bool(suffix), 'httpStatus': response.status,
                               'result': status, 'reason': reason,
                               'headers': {k: safe_detail(v) for k, v in response.headers.items() if k in {'content-type', 'age', 'etag', 'cf-cache-status', 'cf-ray', 'server', 'via', 'cache-control'}}})
        with tempfile.TemporaryDirectory(prefix='rank-rent-public-audit-') as folder:
            downloaded = Path(folder)
            for name in sorted(expected):
                path = routes.path(name) if name in routes.pages else '/' + name
                response = homepage if name == 'index.html' else fetch('https://' + host + path, 16 * 1024 * 1024)
                ok = response.status == 200 and not response.error and not response.truncated
                if ok:
                    target = downloaded / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(response.body)
                    if urlsplit(response.final_url).path != path:
                        issues.append({'code': 'live-public-route', 'host': host, 'page': name, 'severity': 'error', 'detail': 'Public route redirects to a different path'})
                    if any(v in response.headers.get('x-robots-tag', '').lower() for v in ('noindex', 'nofollow', 'noimageindex', 'none')):
                        issues.append({'code': 'live-indexing-header', 'host': host, 'page': name, 'severity': 'error', 'detail': 'Blocking X-Robots-Tag header'})
                    if name not in routes.pages and (output / name).is_file() and hashlib.sha256(response.body).digest() != hashlib.sha256((output / name).read_bytes()).digest():
                        issues.append({'code': 'live-asset-drift', 'host': host, 'page': name, 'severity': 'error', 'detail': 'Public asset differs from local reviewed output'})
                public.append({'host': host, 'path': path, 'httpStatus': response.status, 'result': 'PASS' if ok else 'FAIL'})
            checked = audit(config, downloaded, live=True)
            issues.extend({**i, 'host': host} for i in checked['issues'])
    ready = all(p['result'] == 'PASS' for p in probes + public) and not any(i['severity'] == 'error' for i in issues)
    return {'result': 'PASS' if ready else 'FAIL', 'ready': ready, 'hosts': hosts,
            'privateChecks': probes, 'publicChecks': public, 'issues': issues,
            'limits': 'Read-only samples from this network location, not proof for all paths, caches, regions or routing settings. No calls or form submissions. Homepage HTML with 200 is a safe fallback, not a genuine 404.'}
