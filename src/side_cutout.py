from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from src.packageland import handler


def do_the_thing(path):
    img = Image.open(path)
    w, h = img.size
    ellipse_img = Image.new('L', [w, h], 0)
    draw = ImageDraw.Draw(ellipse_img)
    draw.ellipse([(-w // 1.5, h // 4), (w // 1.5, h * 3 // 4)], fill=255)
    ellipse_img = ellipse_img.filter(ImageFilter.GaussianBlur(50))
    draw = ImageDraw.Draw(ellipse_img)
    draw.rectangle([(0, 0), (10, h)], fill=0)
    ellipse_img = ellipse_img.filter(ImageFilter.GaussianBlur(5))
    img.putalpha(ellipse_img)
    ellipse_img.close()
    img2_path = Path("./diffuse_fatality_blend", path.name)
    img2 = Image.open(img2_path)
    img2.paste(img, mask=img)
    out_path = Path.joinpath(Path("output/diffuse_merged/"), path.stem + ".png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img2.save(out_path, compress_level=1)


if __name__ == '__main__':
    rgb_path = Path('./diffuse_RGB_1-2_4x/')
    rgb_list = list(rgb_path.glob('*.*'))
    parallel = True
    if parallel:
        handler.parallel_process(rgb_list, do_the_thing, 10)
    else:
        handler.solo_process(rgb_list, do_the_thing)
