#!/usr/bin/env python3
"""news-image-20261127 entry: copy the rendered image to the output dir.

The image is rendered by build_image.py (PIL flat editorial illustration,
drawn with shapes only) and committed as entry.png in this repository.
This program just copies it to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output), so both runs write exactly the same bytes.
"""
import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    shutil.copyfile(src, os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
