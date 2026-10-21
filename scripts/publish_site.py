"""Stage validated public output locally. Does not commit, push or deploy."""
import argparse
import json
import shutil
from pathlib import Path

from deployment_security import inspect_output, private_paths
from validate_production import audit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / 'output'


def stage(config, output, destination):
    output, destination = Path(output), Path(destination)
    source, target = output.resolve(), destination.resolve()
    if target == ROOT.resolve() or target == source or target.is_relative_to(source) or source.is_relative_to(target):
        raise ValueError('Use a separate public-only staging directory; repository-root publishing is disabled')
    if destination.is_symlink():
        raise ValueError('Symlinked staging destinations are not supported')
    if not audit(config, output)['ready']:
        raise ValueError('Production validation failed; no files copied')
    if destination.exists():
        if inspect_output(config, destination, ROOT):
            raise ValueError('Destination is not a validated public-only artifact; no files copied')
    else:
        destination.mkdir(parents=True)
    for item in sorted(output.rglob('*')):
        if item.is_file():
            target_file = destination / item.relative_to(output)
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_file)
    print('PASS: validated public output staged locally; nothing committed, pushed or deployed.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site_slug', help='Explicit site slug; legacy default inputs are not used')
    parser.add_argument('--destination', type=Path, required=True, help='Separate public-only directory; never the authoring root')
    args = parser.parse_args(argv)
    private_paths(args.site_slug)
    config = json.loads((ROOT / 'config' / f'config-{args.site_slug}.json').read_text())
    stage(config, OUTPUT_DIR, args.destination)


if __name__ == '__main__':
    main()
