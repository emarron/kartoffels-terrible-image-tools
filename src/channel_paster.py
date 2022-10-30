from PIL import Image
from pathlib import Path
from packageland import handler


def merge_rgb_blue(rgb, blue):
    rgb_img = Image.open(rgb)  # should be "RGB"
    blue_img = Image.open(blue)  # should be "L"
    out_img = Image.merge("RGB", (rgb_img.split()[0], rgb_img.split()[1], blue_img.split()[0]))
    del rgb_img, blue_img
    return out_img


def do_thing_merge(rgb):
    blue = Path("./normal_flat_blue_4x", rgb.name)
    out_image = merge_rgb_blue(rgb, blue)
    out_path = Path.joinpath(Path("output/channel_paster/"), blue.stem + ".png")
    out_image.save(out_path, compress_level=1)


if __name__ == '__main__':
    rgb_path = Path('./normal_flat_rgb_4x/')
    rgb_list = list(rgb_path.glob('*.*'))
    parallel = True
    if parallel:
        handler.parallel_process(rgb_list, do_thing_merge, 10)
    else:
        handler.solo_process(rgb_list, do_thing_merge)
