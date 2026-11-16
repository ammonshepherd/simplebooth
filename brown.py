#!/usr/bin/env python3
"""Photobooth for the Brown College Fall Semi-Formal 2026.

  python brown.py              run the photobooth
  python brown.py --preview    render preview/strip.png and preview/print_sheet.png
                               with sample photos (no camera or printer needed)

To use a different logo, put the file in this folder and change LOGO below.
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.chdir(HERE)                 # simplebooth.py loads its files from here
sys.path.insert(0, str(HERE))

import strip

######################################################################
#     BROWN COLLEGE SETTINGS
######################################################################
strip.LOGO = 'Brown-College-standin-logo.png'
strip.BOTTOM_TEXT = "Brown College\nFall Semi-Formal 2026"

if __name__ == "__main__":
  if "--preview" in sys.argv:
    sys.argv.remove("--preview")
    import preview_strip
    preview_strip.main()
  else:
    import simplebooth  # starts the photobooth
