# SVG to PNG Conversion for Game Icons

Requires ImageMagick: apt-get install -y imagemagick

Basic: convert -background none -density 300 input.svg -resize 128x128 output.png

Flags: -background none (transparent bg), -density 300 (sharpness), -resize 128x128 (target size)

Batch: for svg in *.svg; do convert -background none -density 300 "$svg" -resize 128x128 "${svg%.svg}.png"; done
