import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.generate_gallery import generate_cppn_image

class TestCPPNImage(unittest.TestCase):
    def test_cppn_generation(self):
        pixels, entropy = generate_cppn_image(64, 64, seed=42)
        self.assertEqual(len(pixels), 64)
        self.assertEqual(len(pixels[0]), 64)
        self.assertGreater(entropy, 3.0)

if __name__ == '__main__':
    unittest.main()
