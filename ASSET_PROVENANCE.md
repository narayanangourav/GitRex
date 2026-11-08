# Artwork provenance, permission and limitations

## Primary illustrated assets

- `assets/trex_original.png` — realistic-looking T-Rex sprite used by default
- `assets/forest_original.png` — atmospheric forest backdrop used by default
- `assets/ai_generated_scene_source.png` — **new AI-generated GitRex illustration** created for this release during the present conversation (a crop of the generated illustration), from which these two layers were extracted
- `tools/prepare_illustration.py` — the full **offline extraction/inpainting pipeline** that separates the dinosaur and forest and removes promotional labels
- `output/trex.png` and `output/trex.gif` — generated demo composites from these assets

**Source distinction:** The input to `prepare_illustration.py` is NOT the previously uploaded dinosaur reference image. No old reference photograph, cutout, reconstructed photo background, or online stock asset is included in this release.

The image-generation process was tasked with creating new GitRex artwork, and those outputs were then edited locally. The resulting character has brown textured scales and a scenic forest background, rather than reusing the user's earlier greenish T-Rex picture.

## Fully procedural fallback

For a version drawn entirely from source code without any AI image generator or reference media, the repository also includes:

- `tools/generate_procedural_art.py` — code-authored shapes, scales and forest effects
- `assets/procedural/trex_procedural.png`
- `assets/procedural/forest_procedural.png`

To use the procedural version, replace the two default `assets/*_original.png` files with the corresponding fallback images. The renderer requires no other changes. This alternative is less photorealistic but independently reproducible with only Pillow and Python.

## Rebuild the illustrated layers

```powershell
python -m pip install -r requirements-art.txt
python tools/prepare_illustration.py
```

This only uses an AI-generated source image **already bundled in the repo**. It does not fetch content or call an AI API. OpenCV's GrabCut and inpainting algorithms can vary slightly across versions, so exact pixel hashes across environments are not promised.

## Intellectual-property note

This release contains newly generated or procedurally authored assets, **not knowingly copied third-party files**. That reduces the risk from unclear image provenance, but no one can guarantee that generative artwork is legally exclusive, copyrightable in every jurisdiction, or free from all resemblance claims. Asset ownership and commercial-use rights may depend on the image-generation provider's terms and applicable law. The project license applies only to rights the distributing contributors actually have. Avoid names, logos or descriptions implying affiliation with film franchises.
