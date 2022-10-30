import argparse
from pathlib import Path

from PIL import Image, ImageChops

from packageland import handler

Image.MAX_IMAGE_PIXELS = None

parser = argparse.ArgumentParser(description="ICADM, Image Channel and Directory Modifier")
parser.add_argument('--directory', '-d', metavar='-D', type=str, help='Initial directory to be processed.',
                    required=True)
parser.add_argument('--command', '-c', metavar='-C', type=str,
                    help='split, merge, 4split, 4merge, flatten, unflatten, tga_png (tga_png is destructive!), solid_colors',
                    required=True)
parser.add_argument('--output', '-o', metavar='-O', type=str, default='png', help='output image type, png or tga, '
                                                                                  'default=png')
parser.add_argument('--parallel', '-p', metavar='-P', action=argparse.BooleanOptionalAction,
                    help='multicore processing')
parser.add_argument('--multiplier', '-m', metavar='-M', type=int, default=5,
                    help='if using multicore processing, job multiplier per core. default = 5')
args = parser.parse_args()

if args.directory.endswith('/') or args.directory.endswith('\\'):
    folder = args.directory[:-1]
else:
    folder = args.directory
p = Path(folder)
command = args.command
parallel = args.parallel
multiplier = args.multiplier
output_suffix = args.output.lower()


def save(image, path, suffix=None):
    path.parent.mkdir(exist_ok=True, parents=True)
    if suffix is not None:
        image.save(path.with_suffix(suffix))
    elif output_suffix is not None and output_suffix == 'tga':
        # make this not stupid later
        image.save(path.with_suffix('.tga'))
    else:
        image.save(path.with_suffix('.png'), compress_level=1)


def make_path(path, d_suffix, flat=True):
    out_folder = Path(str(folder) + d_suffix)
    if flat:
        out_path = Path.joinpath(out_folder, flatten_path(path))
    else:
        out_path = Path.joinpath(out_folder, Path(*path.parts[1:]))
    return out_path


def flatten_path(path):
    flattened_path = Path(str(path.parent).replace('\\', '') + path.name)
    return flattened_path


def unflatten_path(path):
    unflattened_path = Path(str(path.parent).replace('😊', '\\') + path.name)
    return unflattened_path


def check_path_exists(path):
    if not path.exists():
        if path.with_suffix('.png').exists():
            path = path.with_suffix('.png')
        if path.with_suffix('.tga').exists():
            path = path.with_suffix('.tga')
    return path


def do_thing_flatten(path):
    """
    flatten dir and save to PNG
    """
    with Image.open(path) as image:
        out_path = make_path(path, '_RGBA')
        save(image.convert('RGBA'), out_path)


def do_thing_unflatten(path):
    flattened_path = make_path(path, '_RGBA')
    try:
        with Image.open(flattened_path) as image:
            merged_path = Path.joinpath(Path('./output'), Path(*path.parts[1:]))
            save(image, merged_path)
    except FileNotFoundError:
        pass


def do_thing_split_RGB_A(path):
    """
    flatten dir, separate RGB and A, and save to PNG
    """
    with Image.open(path) as image:
        rgb_path = make_path(path, '_RGB')
        alpha_path = make_path(path, '_A')
        save(image.convert('RGB'), rgb_path)
        try:
            with image.getchannel('A') as alpha:
                # check if pure white
                if ImageChops.invert(alpha).getbbox():
                    save(alpha, alpha_path)
        except ValueError:
            pass


def do_thing_split_R_G_B_A(path):
    """
    flatten dir, separate R, G, B, A, and save to PNG
    """
    with Image.open(path) as image:
        red_path, green_path, blue_path, alpha_path = [make_path(path, '_R'),
                                                       make_path(path, '_G'),
                                                       make_path(path, '_B'),
                                                       make_path(path, '_A')]
        save(image.getchannel('R'), red_path)
        save(image.getchannel('G'), green_path)
        save(image.getchannel('B'), blue_path)
        try:
            with image.getchannel('A') as alpha:
                if ImageChops.invert(alpha).getbbox():
                    save(alpha, alpha_path)
        except ValueError:
            pass


def do_thing_get_solid_colors(path):
    solid_color_path = make_path(path, '_S', False)
    image = Image.open(path)
    try:
        if len(image.getcolors()) == 1:
            save(image, solid_color_path)
            image.close()
            path.unlink()
        else:
            image.close()
    except TypeError:
        # if color is greater than 256
        image.close()


def do_thing_TGA_PNG(path):
    """
    convert TGA to PNG
    """
    if path.suffix == '.tga':
        image = Image.open(path)
        if not image.mode == 'RGBA':
            image.save(path.with_suffix('.png'), compress_level=1)
            image.close()
            path.unlink()
        else:
            pass


def do_thing_merge_R_G_B_A(path):
    red_path, green_path, blue_path, alpha_path = [make_path(path, '_R'),
                                                   make_path(path, '_G'),
                                                   make_path(path, '_B'),
                                                   make_path(path, '_A')]
    try:
        with Image.merge('RGB', [Image.open(red_path).convert('L'), Image.open(green_path).convert('L'),
                                 Image.open(blue_path).convert('L')]) as image:
            merged_path = make_path(path, '_output', False)
            try:
                with Image.open(alpha_path).convert('L') as alpha:
                    image.putalpha(alpha)
                    save(image, merged_path)
            except FileNotFoundError:
                # could just copy rather than open and save
                save(image, merged_path)
    except FileNotFoundError:
        pass


def do_thing_merge_RGB_A(path):
    rgb_path = make_path(path, '_RGB')
    rgb_path = check_path_exists(rgb_path)
    alpha_path = make_path(path, '_A')
    alpha_path = check_path_exists(alpha_path)
    try:
        with Image.open(rgb_path) as image:
            merged_path = make_path(path, '_output', False)
            try:
                with Image.open(alpha_path).convert('L') as alpha:
                    image.putalpha(alpha)
                    save(image, merged_path)
            except FileNotFoundError:
                # could just copy rather than open and save
                save(image, merged_path)
    except FileNotFoundError:
        pass


def read_command(command):
    if "flatten" == command.lower():
        return do_thing_flatten
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
        return do_thing_unflatten
    if "solid_colors" == command.lower():
        return do_thing_get_solid_colors


if __name__ == '__main__':
    grabber = list(p.glob('**/*.*'))
    function = read_command(command)
    if parallel:
        handler.parallel_process(grabber, function, multiplier)
    else:
        handler.solo_process(grabber, function)
