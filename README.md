# Kartoffels Terrible Image Tools

Scripts for specialized image processing. Mostly related to ffxiv.

## REQUIREMENTS

just run ```pip install -r requirements.txt```

## ICADM, Image Channel and Directory Modifier

Handles two major issues in my workflow, and some other nitpicking.

1. Seperates RGBA images into (RGB, A) or (R, G, B, A).
2. Flattens nested directory structures.

```
usage: icadm.py [-h] --directory -D --command -C [--output -O]

options:

-h, --help      show this help message and exit
--directory     Initial directory to be processed.
--command       split, merge, 4split, 4merge, flatten, unflatten, solid_colors, tga_png (tga_png is destructive!)
--output        output image type, png=default or tga.
```

command descriptions:

flatten, unflatten - flattens/unflattens directory structure.

split, merge - flattens/unflattens directory structure and splits/merges RGBA - (RGB, A) images.

4split, 4merge - same as (split, merge) but with (R, G, B, A) instead of (RGB, A).

solid_colors - read directory gets images that are solid colors and moves them to directory_S.

tga_png - converts all images in directory to png. (DESTRUCTIVE)

## heuristic_filters

Heuristic Filters, Filter images by histogram based heuristics

options:
  -h, --help            show this help message and exit
  --directory -D, -d -D
                        Initial directory to be processed.
  --command -C, -c -C   variance_range, mean_range, stddev_mean
  --parallel, --no-parallel, -p
                        multicore processing
  --threshold -T, -t -T
                        threshold for mean and var range, scalar for stddev, default=0.5
  --multiplier -M, -m -M
                        if using multicore processing, job multiplier per core. default = 5


some operations to hopefully find interesting images when they are not labeled properly.

mean_range: A large difference between the means of each channel can indicate that the channels are being used for
different purposes. threshold should be around 0.1-1.0

variance_range: A large difference between the variances of each channel can indicate the channels are being used
for different purposes. threshold should be from 0.1-1.0

stddev_mean: If the stddev of any channel is greater than the mean of that channel, then the image may have
channel(s) being used for opacity. stddev scalar should be from 0.1-10, where scalar=10 gives 10*stddev, and scalar=0.1
gives stddev/10.

## unique_color_threshold

Reads a directory of images and if the image has greater than $value unique colors, outputs to threshold_matched
directory.

I use it to:

1. seperate ffxiv dye maps from ffxiv opacity maps, value=200ish
2. seperate broken af images, value=2e6 (2 million)
3. seperate ffxiv meaninglessly speckled alphas, value=2

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