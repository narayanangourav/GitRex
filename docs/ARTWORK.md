# GitRex assets and regeneration

GitRex now ships two independently created artwork sets. **Neither depends on the older user-uploaded dinosaur picture.**

## Default realistic illustration (AI-generated source)

`assets/ai_generated_scene_source.png` is a newly generated original GitRex illustration crop. `tools/prepare_illustration.py` separates it into a sprite and forest, then saves `assets/trex_original.png` and `assets/forest_original.png`.

```powershell
python -m pip install -r requirements-art.txt
python tools/prepare_illustration.py
```

OpenCV is optional for normal usage; the ZIP already includes the prepared files. The source image is distributed in the ZIP for reproducibility and provenance review.

## Fully procedural alternative

`tools/generate_procedural_art.py` creates its own T-Rex illustration and forest using only seeded Python/Pillow shapes, gradients, skin scales, trees and atmospheric effects. No AI models, reference images or remote services.

```powershell
python -m pip install -r requirements.txt
python tools/generate_procedural_art.py
```

Outputs are saved under `assets/procedural/`. To use them in the renderer, copy `trex_procedural.png` to `assets/trex_original.png` and `forest_procedural.png` to `assets/forest_original.png`.

Both options are 2D illustrations. The motion engine scales, sways and bounces the whole character; it does not independently rig limbs or the jaw.
