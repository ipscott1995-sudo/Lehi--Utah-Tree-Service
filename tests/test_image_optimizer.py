"""Exercise the optional optimizer with real encoders, without network downloads."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


@unittest.skipUnless(importlib.util.find_spec("PIL"), "Install requirements-images.txt to test the optional optimizer")
class OptimizerTests(unittest.TestCase):
    def test_card_rendition_does_not_upscale_or_stretch(self):
        from PIL import Image
        import optimize_images
        original = Image.new("RGB", (240, 480), "green")
        with tempfile.TemporaryDirectory() as temp, patch.object(optimize_images, "ROOT", Path(temp)):
            variants = optimize_images.build_variants(original, {"aspectRatio": [4, 3], "cropCenter": [0.5, 0.4], "widths": [120, 320]}, [], Path(temp), "portrait-card", 70)
            self.assertEqual([(v["width"], v["height"]) for v in variants], [(120, 90), (240, 180)])
            for variant in variants:
                with Image.open(Path(temp) / variant["path"]) as decoded:
                    self.assertEqual(decoded.format, "WEBP")
                    self.assertEqual(decoded.size, (variant["width"], variant["height"]))
                    self.assertFalse(decoded.getexif())
            self.assertEqual(original.size, (240, 480))

    def test_social_jpeg_has_requested_dimensions(self):
        from PIL import Image
        import optimize_images
        with tempfile.TemporaryDirectory() as temp, patch.object(optimize_images, "ROOT", Path(temp)):
            variants = optimize_images.build_variants(Image.new("RGB", (1600, 1200)), {"aspectRatio": [40, 21], "format": "jpeg", "quality": 85, "widths": [1200]}, [], Path(temp), "social", 70)
            path = Path(temp) / variants[0]["path"]
            with Image.open(path) as decoded:
                self.assertEqual(decoded.format, "JPEG")
                self.assertEqual(decoded.size, (1200, 630))
            self.assertEqual(path.stat().st_size, variants[0]["bytes"])
