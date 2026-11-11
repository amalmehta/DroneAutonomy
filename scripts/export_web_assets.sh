#!/bin/zsh
# Copy the compiled paper and its figures into website/ and docs/images/ (run after compiling the paper).
cd "$(dirname "$0")/.."
venue=paper/drone-autonomy/ieee-conf
cp $venue/main.pdf website/paper.pdf
swift scripts/pdf_to_png.swift $venue/figures/adaptation_curves.pdf website/images/adaptation_curves.png 3
cp website/images/adaptation_curves.png docs/images/adaptation_curves.png
echo "exported paper.pdf and adaptation_curves.png"
