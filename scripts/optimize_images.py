"""Build responsive WebP variants from licensed local sources, without network access."""

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageOps, features

from site_media import local_path

ROOT = Path(__file__).resolve().parents[1]


def build_variants(image, settings, defaults, asset_dir, stem, quality):
    requested = settings.get("widths", defaults)
    if not requested or any(type(w) is not int or w <= 0 for w in requested):
        raise ValueError("Image widths must be positive integers")
    ratio = settings.get("aspectRatio")
    crop = image
    if ratio:
        if len(ratio) != 2 or any(type(n) is not int or n <= 0 for n in ratio):
            raise ValueError("aspectRatio must contain two positive integers")
        center = settings.get("cropCenter", [0.5, 0.5])
        if len(center) != 2 or any(not 0 <= n <= 1 for n in center):
            raise ValueError("cropCenter must contain two numbers from 0 to 1")
        factor = min(image.width / ratio[0], image.height / ratio[1])
        crop = ImageOps.fit(image, (max(1, int(factor * ratio[0])), max(1, int(factor * ratio[1]))),
                            method=Image.Resampling.LANCZOS, centering=tuple(center))
    fmt = settings.get("format", "webp")
    if fmt not in {"webp", "jpeg"}:
        raise ValueError("Rendition format must be webp or jpeg")
    extension = "jpg" if fmt == "jpeg" else "webp"
    variants = []
    for width in sorted({min(w, crop.width) for w in requested}):
        height = max(1, round(crop.height * width / crop.width))
        resized = crop.resize((width, height), Image.Resampling.LANCZOS)
        target = asset_dir / f"{stem}-{width}.{extension}"
        options = {"quality": settings.get("quality", quality)}
        if type(options["quality"]) is not int or not 1 <= options["quality"] <= 100:
            raise ValueError("Image quality must be an integer from 1 to 100")
        options.update({"optimize": True, "progressive": True} if fmt == "jpeg" else {"method": 6})
        resized.save(target, "JPEG" if fmt == "jpeg" else "WEBP", **options)
        variants.append({"path": target.relative_to(ROOT).as_posix(), "width": width,
                         "height": height, "bytes": target.stat().st_size})
    return variants


def optimize(manifest_path: Path, quality: int = 78):
    if not features.check("webp"):
        raise RuntimeError("Pillow needs WebP support")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("version") != 1:
        raise ValueError("Unsupported image manifest version")
    for image_id, item in manifest["images"].items():
        source_path = local_path(ROOT, item["original"], "assets/images")
        stem = item["filename"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", stem):
            raise ValueError(f"Unsafe image filename: {stem}")
        asset_dir = local_path(ROOT, manifest["assetDirectory"], "images/optimized")
        asset_dir.mkdir(parents=True, exist_ok=True)
        with Image.open(source_path) as raw:
            image = ImageOps.exif_transpose(raw).convert("RGB")
            item["originalDimensions"] = {"width": image.width, "height": image.height}
            item["originalSha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
            variants = build_variants(image, item, manifest.get("widths", [400, 800, 1200, 1600]), asset_dir, stem, quality)
            item["variants"] = variants
            for name, rendition in item.get("renditions", {}).items():
                if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
                    raise ValueError("Unsafe rendition name")
                rendition["variants"] = build_variants(image, rendition, [400, 600, 800], asset_dir, f"{stem}-{name}", quality)
                rendition["modifications"] = "Cropped to configured aspect ratio; resized, compressed and metadata removed."
            item["modifications"] = "Resized and compressed as WebP; metadata removed."
            print(f"{image_id}: " + ", ".join(f'{v["width"]}w/{v["bytes"] // 1024} KiB' for v in variants))
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="Manifest path relative to project root")
    parser.add_argument("--quality", type=int, default=78)
    args = parser.parse_args()
    if not 1 <= args.quality <= 100:
        parser.error("quality must be 1–100")
    optimize(local_path(ROOT, args.manifest, "config"), args.quality)
