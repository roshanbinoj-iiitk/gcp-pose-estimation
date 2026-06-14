#!/usr/bin/env python3
"""Build CV.ipynb from cell parts."""
import json, glob, os

cells = []
# Read cell files in order
for f in sorted(glob.glob("nb_cells/cell_*.py")):
    with open(f) as fh:
        src = fh.read()
    # Check if it starts with #MARKDOWN
    if src.startswith("#MARKDOWN\n"):
        md_text = src[len("#MARKDOWN\n"):]
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [l + "\n" for l in md_text.rstrip("\n").split("\n")]
        })
    else:
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [l + "\n" for l in src.rstrip("\n").split("\n")]
        })
    # Strip trailing \n from last source line
    if cells[-1]["source"]:
        cells[-1]["source"][-1] = cells[-1]["source"][-1].rstrip("\n")

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py", "mimetype": "text/x-python",
            "name": "python", "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3", "version": "3.11.15"
        }
    },
    "nbformat": 4, "nbformat_minor": 5
}

with open("CV.ipynb", "w") as f:
    json.dump(nb, f, indent=1)
print(f"Built CV.ipynb with {len(cells)} cells")
