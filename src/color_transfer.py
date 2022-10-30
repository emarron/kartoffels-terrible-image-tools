from pathlib import Path
from PIL import Image

from packageland import handler


def color_transfer(ref_img, in_img):
    """
    Designed for grayscale images. Corrects input image's palette to the 16 most used values of
    reference image's palette. There is a faster way to do this, but eh.

    """
    ref_colors = ref_img.getcolors()
    ref_colors.sort(reverse=True)
    # ref_palette = [color[1] for color in ref_colors[:16]]
    ref_palette = [color[1] for color in ref_colors]
    out_data = []
    for color in in_img.getdata():
        new_color = min(ref_palette, key=lambda palette_color: abs(palette_color - color))
        out_data.append(new_color)

    out_img = Image.new(in_img.mode, in_img.size)
    out_img.putdata(out_data)
    return out_img


def do_the_thing(input_path):
    reference_path = Path('./reference') / input_path.relative_to(*input_path.parts[:1]).with_name(
        input_path.stem + '.png')
    input_image = Image.open(input_path)
    reference_image = Image.open(reference_path)
    if input_image.mode == 'RGB':
        input_image.convert('L')
    if reference_image.mode == 'RGB':
        reference_image.convert('L')

    output_image = color_transfer(reference_image, input_image)
    output_path = Path.joinpath(
        Path('./output'),
        (input_path.relative_to(*input_path.parts[:1]).with_name(input_path.stem + '.png')))
    output_path.parent.mkdir(exist_ok=True, parents=True)
    output_image.save(output_path)


if __name__ == '__main__':
    inputs_path = Path('./input')
    input_list = list(inputs_path.glob('**/*.*'))
    parallel = True
    if parallel:
        handler.parallel_process(input_list, do_the_thing, 1)
    else:
        handler.solo_process(input_list, do_the_thing)
