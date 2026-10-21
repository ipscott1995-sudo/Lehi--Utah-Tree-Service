"""Serve a local build with configured public routes; never deploys anything."""
import argparse
import functools
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from site_urls import SiteURLs

ROOT = Path(__file__).resolve().parents[1]


class SiteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, routes, **kwargs):
        self.routes = routes
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        filename = self.routes.physical(urlsplit(path).path)
        return super().translate_path('/' + filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site_slug')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    config = json.loads((ROOT / 'config' / f'config-{args.site_slug}.json').read_text())
    handler = functools.partial(SiteHandler, routes=SiteURLs(config), directory=str(ROOT / 'output'))
    print(f'Local build: http://localhost:{args.port}/', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), handler).serve_forever()
