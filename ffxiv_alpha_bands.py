import gc
from pathlib import Path

import numpy as np
from PIL import Image

from packageland import handler

Image.MAX_IMAGE_PIXELS = None


def to_bands(img: Image.Image):
    # WRITTEN BY SINOM
    alpha = np.array(img.split()[3])
    in_range = lambda array, min, max: (array >= min) & (array <= max)

    values_lo = [0x11, 0x33, 0x55, 0x77, 0x99, 0xBB, 0xDD]

    mid = 0x11 // 2
    # bad ranges masks
    u_masks = [in_range(alpha, a + 1, (a + 0x11) - mid) for a in values_lo]
    d_masks = [in_range(alpha, a + mid, (a + 0x11) - 1) for a in values_lo]
    # good ranges masks
    masks = [in_range(alpha, a, a + 0x11) for a in [x * 0x22 for x in range(0, 8)]]

    bands = [np.zeros(alpha.shape, alpha.dtype) for _ in range(0, 8)]
    white = np.full(alpha.shape, 255, alpha.dtype)

    for i, mask in enumerate(masks):
        np.putmask(bands[i], mask, white)

    for i, mask in enumerate(u_masks):
        np.putmask(bands[i], mask, white)

    for i, mask in enumerate(d_masks):
        np.putmask(bands[i + 1], mask, white)

    rgba = []
    for band in bands:
        band = Image.fromarray(band, 'L')
        rgba.append(Image.merge("RGBA", (img.split()[3], img.split()[3], img.split()[3], band)))

    return rgba


def paste_bands(source, bands):
    for band in bands:
        source.paste(band, (0, 0), band)
    gc.collect()
    return source


def do_thing_paste(dir):
    XBR_bands = []
    paths = list(dir.glob("*"))
    threshold = 254  # theoretically might need this later
    for path in paths:
        with Image.open(path) as image:
            try:
                alpha = image.split()[3]
                alpha = alpha.point(lambda p: p > threshold and 255)
                image.putalpha(alpha)
            except IndexError:
                pass
            XBR_bands.append(image)
    output_image = paste_bands(XBR_bands[8], XBR_bands[:8])
    del XBR_bands
    output_image.save("output/" + str(dir.name) + ".png", compress_level=1)
    output_image.close()
    gc.collect()


# normals_path = Path('./input')
# normals_list = list(normals_path.glob('**/*.*'))
# for path in tqdm(normals_list, desc="Folders Processed"):
#     image = Image.open(path)
#     bands = to_bands(image)
#     alpha = (image.split()[3])
#     output_path = Path.joinpath(Path('./output'), path.stem)
#     output_path.mkdir(exist_ok=True, parents=True)
#     alpha.save(Path.joinpath(output_path, path.stem + ".png"))
#     for i, band in enumerate(bands):
#         band.save(Path.joinpath(output_path, Path(str(i) + ".png")))

if __name__ == '__main__':
    XBR_path = Path('./xbr_4x_blend/')
    XBR_directories = list(filter(lambda path: path.is_dir(), XBR_path.glob('*')))
    parallel = True
    if parallel:
        handler.parallel_process(XBR_directories, do_thing_paste, 1)
    else:
        handler.solo_process(XBR_directories, do_thing_paste)
