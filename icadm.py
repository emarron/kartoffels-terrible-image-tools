import sys
from pathlib import Path

from PIL import Image, ImageChops

from packageland import handler

if sys.argv[1].endswith('/') or sys.argv[1].endswith('\\'):
    folder = sys.argv[1][:-1]
else:
    folder = sys.argv[1]
p = Path(folder)
command = sys.argv[2]


def flatten_path(path):
    flattened_path = Path(str(path.parent).replace('\\', '') + path.stem + ".png")
    return flattened_path


def unflatten_path(path):
    unflattened_path = Path(str(path.parent).replace('😊', '\\') + path.name)
    return unflattened_path


def do_thing_flatten_PNG(path):
    """
    flatten dir and save to PNG
    """
    with Image.open(path) as image:
        out_folder = Path(str(folder) + '_RGBA')
        out_path = Path.joinpath(out_folder, flatten_path(path))
        out_path.parent.mkdir(exist_ok=True, parents=True)
        image.convert('RGBA').save(out_path.with_suffix('.png'), compress_level=1)


def do_thing_unflatten_PNG(path):
    flattened_folder = Path(str(folder) + '_RGBA')
    flattened_path = Path.joinpath(flattened_folder, flatten_path(path))
    try:
        with Image.open(flattened_path) as image:
            merged_path = Path.joinpath(Path('./output'), Path(*path.parts[1:]).with_suffix(".tga"))
            merged_path.parent.mkdir(exist_ok=True, parents=True)
            image.save(merged_path)
    except FileNotFoundError:
        pass


def do_thing_split_RGB_A(path):
    """
    flatten dir, separate RGB and A, and save to PNG
    """
    with Image.open(path) as image:
        rgb_folder, alpha_folder = [Path(str(folder) + '_RGB'), Path(str(folder) + '_A')]
        rgb_path = Path.joinpath(rgb_folder, flatten_path(path))
        alpha_path = Path.joinpath(alpha_folder, flatten_path(path))
        rgb_path.parent.mkdir(exist_ok=True, parents=True)
        alpha_path.parent.mkdir(exist_ok=True, parents=True)
        image.convert('RGB').save(rgb_path.with_suffix('.png'), compress_leve=1)
        try:
            with image.getchannel('A') as alpha:
                if ImageChops.invert(alpha).getbbox():
                    alpha.save(alpha_path.with_suffix('.png'), compress_level=1)
        except ValueError:
            pass


def do_thing_split_R_G_B_A(path):
    """
    flatten dir, separate R, G, B, A, and save to PNG
    """
    with Image.open(path) as image:
        # todo: first part to function.
        red_folder, green_folder, blue_folder, alpha_folder = [Path(str(folder) + 'R'), Path(str(folder) + 'G'),
                                                               Path(str(folder) + 'B'), Path(str(folder) + 'A')]
        red_path, green_path, blue_path, alpha_path = [Path.joinpath(red_folder, flatten_path(path)),
                                                       Path.joinpath(green_folder, flatten_path(path)),
                                                       Path.joinpath(blue_folder, flatten_path(path)),
                                                       Path.joinpath(alpha_folder, flatten_path(path))]
        red_path.parent.mkdir(exist_ok=True, parents=True)
        green_path.parent.mkdir(exist_ok=True, parents=True)
        blue_path.parent.mkdir(exist_ok=True, parents=True)
        image.getchannel('R').save(red_path.with_suffix('.png'), compress_leve=1)
        image.getchannel('G').save(green_path.with_suffix('.png'), compress_leve=1)
        image.getchannel('B').save(blue_path.with_suffix('.png'), compress_leve=1)
        try:
            with image.getchannel('A') as alpha:
                if ImageChops.invert(alpha).getbbox():
                    alpha_path.parent.mkdir(exist_ok=True, parents=True)
                    alpha.save(alpha_path.with_suffix('.png'), compress_level=1)
        except ValueError:
            pass


def do_thing_TGA_PNG(path):
    """
    convert TGA to PNG
    """
    if path.suffix == '.tga':
        with Image.open(path) as image:
            image.save(path.with_suffix('.png'), compress_level=1)
        path.unlink()


def do_thing_merge_R_G_B_A(path):
    red_folder, green_folder, blue_folder, alpha_folder = [Path(str(folder) + 'R'), Path(str(folder) + 'G'),
                                                           Path(str(folder) + 'B'), Path(str(folder) + 'A')]
    red_path, green_path, blue_path, alpha_path = [Path.joinpath(red_folder, flatten_path(path)),
                                                   Path.joinpath(green_folder, flatten_path(path)),
                                                   Path.joinpath(blue_folder, flatten_path(path)),
                                                   Path.joinpath(alpha_folder, flatten_path(path))]
    try:
        with Image.merge('RGB', [Image.open(red_path).convert('L'), Image.open(green_path).convert('L'),
                                 Image.open(blue_path).convert('L')]) as image:
            merged_path = Path.joinpath(Path('./output'), Path(*path.parts[1:]).with_suffix(".tga"))
            merged_path.parent.mkdir(exist_ok=True, parents=True)
            try:
                with Image.open(alpha_path).convert('L') as alpha:
                    image.putalpha(alpha)
                    image.save(merged_path)
            except FileNotFoundError:
                # could just copy rather than open and save
                image.save(merged_path)
    except FileNotFoundError:
        pass


def do_thing_merge_RGB_A(path):
    rgb_folder, alpha_folder = [Path(str(folder) + '_RGB'), Path(str(folder) + '_A')]
    rgb_path = Path.joinpath(rgb_folder, flatten_path(path))
    alpha_path = Path.joinpath(alpha_folder, flatten_path(path))
    try:
        with Image.open(rgb_path) as image:
            merged_path = Path.joinpath(Path('./output'), Path(*path.parts[1:]).with_suffix(".tga"))
            merged_path.parent.mkdir(exist_ok=True, parents=True)
            try:
                with Image.open(alpha_path).convert('L') as alpha:
                    image.putalpha(alpha)
                    image.save(merged_path)
            except FileNotFoundError:
                # could just copy rather than open and save
                image.save(merged_path)
    except FileNotFoundError:
        pass


def read_command(command):
    if "flatten" == command.lower():
        return do_thing_flatten_PNG
    if "split" == command.lower():
        return do_thing_split_RGB_A
    if "merge" == command.lower():
        return do_thing_merge_RGB_A
    if "tga_png" == command.lower():
        return do_thing_TGA_PNG
    if "4split" == command.lower():
        return do_thing_split_R_G_B_A
    if "4merge" == command.lower():
        return do_thing_merge_R_G_B_A
    if "unflatten" == command.lower():
        return do_thing_unflatten_PNG


if __name__ == '__main__':
    grabber = list(p.glob('**/*.*'))
    function = read_command(command)
    parallel = True
    if parallel:
        handler.parallel_process(grabber, function, 5)
    else:
        handler.solo_process(grabber, function)
