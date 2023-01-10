# Kartoffels Terrible Image Tools

Scripts for specialized image processing. Mostly related to ffxiv.

## REQUIREMENTS

just run ```pip install -r requirements.txt```

## ICADM, Image Channel and Directory Modifier

Handles two major issues in my workflow, and some other nitpicking.

1. Seperates RGBA images into (RGB, A) or (R, G, B, A).
2. Flattens nested directory structures.

```
ICADM, Image Channel and Directory Modifier

options:
  -h, --help            show this help message and exit
  --directory -D, -d -D
                        Initial directory to be processed.
  --command -C, -c -C   split, merge, alpha_merge, tga_png (destructive), 4split, 4merge, unflatten, unflatten_rgba, flatten, solid_colors, rgb_gray_Fix, rgb_gray, gray_rgb, alpha_merge
  --parallel, --no-parallel, -p
                        multicore processing
  --multiplier -M, -m -M
                        if using multicore processing, job multiplier per core. default = 5

```

command descriptions:

- flatten, unflatten - flattens/unflattens directory structure
- unflatten_RGBA - flattens directory structure and converts to PNG, but ignores images without A channel.
- split, merge - flattens/unflattens directory structure and
  splits/merges RGBA - (RGB, A) images.
- alpha_merge - merges (RGB, A) but only if A channel exists.
- 4split, 4merge - same as (split, merge) but with (R, G, B, A) instead
  of (RGB, A).
- solid_colors - read directory gets images that are solid colors and
  moves them to directory_S.
- tga_png - converts all images in directory to png. (DESTRUCTIVE)
- gray_rgb - converts from grayscale to rgb by filling each channel
  with the grayscale channel. This is method is useful for passing very
  sensitive grayscale images through tools that would convert the
  grayscale to RGB internally using their 'weighted' conversion. See
  opencv2 GRAY2RGB weighting.
- rgb_gray - converts from rgb to gray IF red channel = green channel.
  This is how I convert back to grayscale. If my work is done properly
  the red channel WILL equal (or close enough, see numpy array
  comparison options) the green channel.
- rgb_gray_fix - this can 'adjust' weighted opencv2 GRAY2RGB to match
  my gray_rgb command output.

## heuristic_filters

Heuristic Filters, Filter images by histogram based heuristics

```
usage: heuristic_filters.py [-h] --directory -D --command -C [--parallel | --no-parallel | -p] [--threshold -T] [--multiplier -M] [--operator -O]

Heuristic Filters, Filter images by histogram based heuristics

options:
  -h, --help            show this help message and exit
  --directory -D, -d -D
                        Initial directory to be processed.
  --command -C, -c -C   variance_range, mean_range, stddev_mean. mean_threshold, median_mean, unique_colors, f_test
  --parallel, --no-parallel, -p
                        multicore processing
  --threshold -T, -t -T
                        threshold between 0 and 1 for variance_range and mean_range, else 0 to 255, default=0.5
  --multiplier -M, -m -M
                        if using multicore processing, job multiplier per core. default = 5
  --operator -O, -o -O  use bash integer comparison style, i.e "gt","lt", default = "gt"

```

some operations to hopefully find interesting images when they are not labeled properly.

Multi channel only:

- mean_range: Check if range of means of the channels is (operator)
  threshold. range is normalized to 0-1.
- variance_range: Check if range
  of variances of the channels is (operator) threshold. range is
  normalized to 0-1.

Both single channel and multi channel:

- unique_color_threshold: Checks if image has greater than threshold
  unique colors. I use it to either separate ffxiv dye maps from ffxiv
  opacity maps (value=200ish), or separate broken af images (value=2e6
  (2 million))
- stddev_mean: Check if stddev is (operator) than mean.
- median_mean: Check if stddev is (operator) than mean. mode_mean:
  Check if mode is (operator) than mean.
- threshold_mean: Check if threshold is (operator) than mean.

## ffxiv_alpha_bands

Reading:

Reads ffxiv normal maps, outputs the dye map and each band of the dye map from 0-7.

Writing:

Reads dye map and each band of the dye map from 0-7, outputs a composite dye map.

why?:

Blending within a band is permitted, but blending outside a band leads to rainbow spaghetti.
I use this to get the dye map and each band of the dye map to process externally.

Dye map: XBR no blend on the dye map, and set it as a background.

Bands: Pixel blending filter (usually XBR blend) on the bands, and overlay them onto the background in order.