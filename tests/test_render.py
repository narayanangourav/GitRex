import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from gitrex.render import PACKAGE_ROOT,render

class RenderTests(unittest.TestCase):
    def test_output_files_and_animation(self):
        snap=json.loads((PACKAGE_ROOT/'assets'/'demo_snapshot.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            result=render(snap,Path(temp),width=360,frames=4)
            for key in ('gif','png','preview','summary'):
                self.assertTrue(Path(result[key]).exists())
            with Image.open(result['gif']) as image:
                self.assertEqual(image.n_frames,4)
                self.assertEqual(image.size,(360,240))
            self.assertIn('Apex Rex',(Path(temp)/'summary.json').read_text())
    def test_invalid_width(self):
        snap=json.loads((PACKAGE_ROOT/'assets'/'demo_snapshot.json').read_text())
        with self.assertRaises(ValueError):render(snap,Path('output'),width=99)

if __name__=='__main__':unittest.main()
