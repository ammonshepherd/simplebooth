# Simple Booth

Intended to be a really simple Python based Photobooth solution.
Mainly because I couldn't get the other options to work nicely with my printer.


# Running the booth
- `python simplebooth.py` runs the booth with the default Scholars' Lab logo and text.
- `python brown.py` runs it for the Brown College Fall Semi-Formal.
- Add `--preview` to an event script (or run `python preview_strip.py`) to render
  the strip and print sheet into `preview/` without the camera or printer.

The strip layout, default logo/text and printer alignment
(`PRINT_OFFSET_X/Y`, `BOTTOM_TEXT_MARGIN`) are in `strip.py`. For a new event,
copy `brown.py`, rename it, and change the logo and text.

# Other options
- pibooth: https://documentation.pibooth.org/en/latest/
- https://www.hackster.io/ericBcreator/photo-booth-powered-by-a-raspberry-pi-23b491
- https://github.com/sabat54i/photoboothdiy


# helpful sites
- https://gpiozero.readthedocs.io/en/stable/recipes.html#button-controlled-camera