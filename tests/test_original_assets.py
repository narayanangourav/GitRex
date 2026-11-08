import unittest
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

class OriginalArtworkTests(unittest.TestCase):
    def test_original_files_exist(self):
        for filename in ('trex_original.png','forest_original.png'):
            self.assertTrue((ROOT/'assets'/filename).is_file())
    def test_no_old_image_assets(self):
        for filename in ('trex_reference.png','trex_cutout.png','forest_clean.jpg'):
            self.assertFalse((ROOT/'assets'/filename).exists())
    def test_alpha_sprite_and_background(self):
        with Image.open(ROOT/'assets'/'trex_original.png') as image:
            self.assertEqual(image.mode,'RGBA')
            self.assertLess(image.getpixel((0,0))[3],5)
            self.assertGreater(image.getchannel('A').getbbox()[2],1000)
        with Image.open(ROOT/'assets'/'forest_original.png') as image:
            self.assertEqual(image.size,(1200,800))
    def test_ai_generated_source_present(self):
        self.assertTrue((ROOT/'assets'/'ai_generated_scene_source.png').is_file())
    def test_original_procedural_fallback(self):
        for name in ('trex_procedural.png','forest_procedural.png'):
            self.assertTrue((ROOT/'assets'/'procedural'/name).is_file())
    def test_reproducible_source_present(self):
        self.assertTrue((ROOT/'tools'/'generate_procedural_art.py').is_file() and (ROOT/'tools'/'prepare_illustration.py').is_file())

if __name__=='__main__': unittest.main()
