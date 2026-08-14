import os
import subprocess
import sys
import tempfile
import unittest

# Permite `from scripts.generate_gallery import ...` cuando se ejecuta
# `python -m unittest` desde la raíz.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.generate_gallery import (
    ACTIVATIONS,
    generate_cppn_image,
    save_pgm,
    save_png,
)

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class TestCPPNImage(unittest.TestCase):
    def test_dimensions_and_entropy(self):
        """El test original: dimensiones correctas y entropía > 3.0."""
        pixels, entropy, meta = generate_cppn_image(64, 64, seed=42)
        self.assertEqual(len(pixels), 64)
        self.assertEqual(len(pixels[0]), 64)
        self.assertGreater(entropy, 3.0)
        self.assertEqual(meta["width"], 64)
        self.assertEqual(meta["height"], 64)
        self.assertEqual(meta["seed"], 42)

    def test_seed_reproducibility(self):
        """Misma semilla produce misma imagen y entropía."""
        p1, e1, _ = generate_cppn_image(32, 32, seed=123)
        p2, e2, _ = generate_cppn_image(32, 32, seed=123)
        self.assertAlmostEqual(e1, e2, places=6)
        self.assertEqual(p1, p2)

    def test_seed_variation(self):
        """Semillas distintas producen imágenes distintas."""
        p1, e1, _ = generate_cppn_image(64, 64, seed=1)
        p2, e2, _ = generate_cppn_image(64, 64, seed=2)
        self.assertNotEqual(p1, p2)

    def test_activations_include_softsign(self):
        """El README promete softsign entre las activaciones."""
        names = [getattr(f, "__name__", "") for f in ACTIVATIONS]
        # Acepta tanto `softsign` como `_softsign` (interno).
        self.assertTrue(
            any("softsign" in n for n in names),
            f"Falta softsign: {names}",
        )

    def test_save_pgm(self):
        """Exportador .pgm (retrocompat)."""
        pixels, _, _ = generate_cppn_image(32, 32, seed=99)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.pgm")
            save_pgm(pixels, path, 32, 32)
            with open(path) as f:
                head = f.readline().strip()
            self.assertEqual(head, "P2")

    @unittest.skipUnless(HAS_PIL, "Pillow no disponible")
    def test_save_png(self):
        """Exportador PNG con Pillow."""
        pixels, _, _ = generate_cppn_image(48, 48, seed=7)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.png")
            save_png(pixels, path, 48, 48)
            img = Image.open(path)
            self.assertEqual(img.size, (48, 48))
            self.assertEqual(img.mode, "RGB")

    @unittest.skipUnless(HAS_PIL, "Pillow no disponible")
    def test_cli_batch(self):
        """La CLI genera --count sueños y crea INDEX.txt con --update-index."""
        repo = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with tempfile.TemporaryDirectory() as tmp:
            cmd = [
                sys.executable,
                os.path.join(repo, "scripts", "generate_gallery.py"),
                "--count", "3",
                "--width", "32",
                "--height", "32",
                "--format", "png",
                "--out-dir", tmp,
                "--update-index",
                "--seed-base", "1000",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, msg=res.stderr)
            files = sorted(os.listdir(tmp))
            pngs = [f for f in files if f.endswith(".png")]
            self.assertEqual(len(pngs), 3)
            self.assertIn("INDEX.txt", files)
            with open(os.path.join(tmp, "INDEX.txt")) as f:
                lines = [l.strip() for l in f if l.strip()]
            self.assertEqual(len(lines), 3)


if __name__ == "__main__":
    unittest.main()
