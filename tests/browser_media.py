"""Local browser smoke checks; no requests to production or external services."""
import argparse
import functools
import json
import threading
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


sys.path.insert(0, str(ROOT / 'scripts'))
from preview_site import SiteHandler
from site_urls import SiteURLs


class QuietHandler(SiteHandler):
    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chrome', help='Optional existing Chrome executable')
    parser.add_argument('--artifacts', default='/tmp/rank-rent-browser-results')
    parser.add_argument('--production', action='store_true', help='Verify standard output has no sample reviews or preview noindex')
    args = parser.parse_args()
    artifacts = Path(args.artifacts)
    artifacts.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT / 'output'), routes=SiteURLs(json.loads((ROOT / 'config/config-lehi-tree-pros.json').read_text()))))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'
    config = json.loads((ROOT / 'config/config-lehi-tree-pros.json').read_text())
    results = []
    errors = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=args.chrome, headless=True)
            for width, height, dpr in [(375,812,1), (584,1000,1), (768,1024,1), (868,1000,1), (900,1000,1), (901,1000,1), (1152,1000,1), (1440,1000,1), (375,812,2), (1440,1000,2)]:
                page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=dpr)
                # Local tests never submit a form, place a call, or load production resources.
                page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(base + '/') else route.abort())
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('response', lambda response: errors.append(f'{response.status} {response.url}') if response.status >= 400 else None)
                for name in ['index.html', 'about.html', 'contact.html', 'faq.html'] + [s['url'] for s in config['services']] + [s['url'] for s in config['locationPages']]:
                    response = page.goto(base + SiteURLs(config).path(name), wait_until='networkidle')
                    assert response.status == 200
                    assert page.locator('link[rel=canonical]').get_attribute('href') == SiteURLs(config).absolute(name)
                    # Scroll to trigger all lazy images before checking decoding.
                    for locator in page.locator('img').all():
                        locator.scroll_into_view_if_needed()
                        locator.evaluate('(img) => img.decode()')
                    checks = page.evaluate('''() => ({
                        width: innerWidth,
                        documentWidth: document.documentElement.scrollWidth,
                        images: [...document.images].map(img => {
                            const hint = img.sizes.split(',').map(x => x.trim()).find(x => !x.startsWith('(') || matchMedia(x.slice(0, x.indexOf(')') + 1)).matches);
                            const length = hint.startsWith('(') ? hint.slice(hint.indexOf(')') + 1).trim() : hint;
                            const probe = document.createElement('div');
                            Object.assign(probe.style, {position:'fixed', visibility:'hidden', width:length, height:'0', border:'0', padding:'0'});
                            document.body.append(probe); const declaredWidth = probe.getBoundingClientRect().width; probe.remove();
                            return {src: img.currentSrc, width: img.naturalWidth, alt: img.alt, declaredWidth, box: img.getBoundingClientRect().toJSON()};
                        }),
                        credits: document.querySelectorAll('.site-image figcaption').length,
                        social: document.querySelector('meta[property="og:image"]')?.content,
                        twitter: document.querySelector('meta[name="twitter:image"]')?.content,
                        h1: document.querySelectorAll('h1').length,
                        reviews: document.querySelectorAll('.review-card').length,
                        sampleLabels: [...document.querySelectorAll('.review-label')].map(x => x.textContent),
                        heroPriority: document.querySelector('.site-image--hero img')?.fetchPriority,
                        noindex: document.querySelector('meta[name="robots"]')?.content
                    })''')
                    assert checks['documentWidth'] <= width, f'Horizontal overflow: {name} at {width}: {checks}'
                    assert checks['credits'] == 0
                    assert checks['social'] == checks['twitter']
                    assert checks['social'].startswith('https://' + config['business']['domain'] + '/')
                    assert all(abs(i['declaredWidth'] - i['box']['width']) < 1 for i in checks['images']), f'Sizes mismatch: {name} at {width}: {checks}'
                    assert checks['h1'] == (2 if name == 'contact.html' else 1)
                    assert all(i['width'] > 0 and i['alt'].strip() for i in checks['images'])
                    if args.production:
                        assert not checks['noindex'] or not any(x in checks['noindex'].lower() for x in ['noindex', 'nofollow'])
                        assert checks['reviews'] == 0
                        assert checks['sampleLabels'] == []
                        assert page.locator('.testimonial, .testimonials-grid, [data-review-mode="sample"]').count() == 0
                    else:
                        assert checks['noindex'] == 'noindex, nofollow'
                        expected_reviews = len(config.get('reviews', {}).get('items', [])) if config.get('reviews', {}).get('mode') == 'sample' and name == 'index.html' else 0
                        assert checks['reviews'] == expected_reviews
                    social_dimensions = page.evaluate('''async () => {
                        const remote = new URL(document.querySelector('meta[property="og:image"]').content);
                        const image = new Image(); image.src = new URL(remote.pathname, location.origin).href;
                        await image.decode(); return [image.naturalWidth, image.naturalHeight];
                    }''')
                    assert social_dimensions == [1200, 630]
                    if name == 'index.html':
                        assert checks['heroPriority'] == 'high'
                        assert all('SAMPLE' in label and 'demonstration' in label for label in checks['sampleLabels'])
                        if width < 900:
                            page.locator('.hamburger').click()
                            assert page.locator('.hamburger').get_attribute('aria-expanded') == 'true'
                            assert page.locator('#mobile-nav').is_visible()
                            page.locator('.hamburger').click()
                        page.locator('.hero-phone-link').scroll_into_view_if_needed()
                        assert page.locator('.hero-phone-link').get_attribute('href') == 'tel:' + config['business']['phoneTel']
                        assert page.locator('.hero-btns a').first.get_attribute('href') == config['business']['formUrl']
                        page.evaluate('window.scrollTo(0,0)')
                        page.screenshot(path=str(artifacts / f'home-{width}-dpr{dpr}.png'), full_page=True)
                    elif name == 'tree-trimming.html':
                        page.evaluate('window.scrollTo(0,0)')
                        page.screenshot(path=str(artifacts / f'trimming-{width}-dpr{dpr}.png'), full_page=True)
                    results.append({'page': name, 'dpr': dpr, **checks})
                page.close()
            browser.close()
        assert not errors, errors
        (artifacts / 'results.json').write_text(json.dumps(results, indent=2))
        mode = 'production (no reviews/no preview indexing directives)' if args.production else 'preview (samples homepage only)'
        print(f'PASS: {len(results)} page/viewport checks; images and local sharing assets decode; no horizontal overflow, page errors or HTTP failures; GHL/call links preserved; {mode}. Artifacts: {artifacts}')
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
