from PIL import Image
from pathlib import Path
from packageland import handler


def merge_rgb_blue(rgb, blue):
    try:
        blue_img = Image.open(blue).convert('L')  # should be "L"
        rgb_img = Image.open(rgb).convert('RGB')  # should be "RGB"
        r = rgb_img.getchannel(0)
        g = rgb_img.getchannel(1)
        b = blue_img.getchannel(0)
        out_img = Image.merge("RGB", (r, g, b))
        del rgb_img, blue_img
        return out_img
    except FileNotFoundError:
        pass


def do_thing_merge(rgb):
    blue = Path("./bg_n_B_S_4x", rgb.name)
    out_image = merge_rgb_blue(rgb, blue)
    if out_image is not None:
        out_path = Path.joinpath(Path("output/bg_n_RGB_4x/"), blue.stem + ".png")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_image.save(out_path, compress_level=1)


if __name__ == '__main__':
    rgb_path = Path('./bg_n_RGB_4x/')
    rgb_list = list(rgb_path.glob('*.*'))
    parallel = True
    if parallel:
        handler.parallel_process(rgb_list, do_thing_merge, 10)
    else:
        handler.solo_process(rgb_list, do_thing_merge)
