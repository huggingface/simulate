# In order to use run this, you will need to change fast-wfc implementation to
# accept an extra argument
# This is a temporary fix to extract a gif showing generated maps
# increasing in size

import argparse
import os

import imageio
import numpy as np
import pyvista as pv
from xland import gen_setup
from xland.utils import create_2d_map
from xland.world import generate_map


def apply_texture_and_bottom(scene):
    """
    Apply texture and add a bottom to map mesh.

    It's done directly on pyvista mesh, since texture is not completely done for scenes yet.
    """
    # Add bottom at first
    sg = scene.top_surface
    sg.mesh.texture_map_to_plane(inplace=True)
    top = sg.mesh.points.copy()
    bottom = sg.mesh.points.copy()

    # Set bottom plane
    bottom[:, -1] = -10.0

    # Create a new grid with an extra column with texture
    processed_grid = pv.StructuredGrid()
    processed_grid.points = np.vstack((top, bottom))
    processed_grid.dimensions = [*sg.mesh.dimensions[0:2], 2]
    processed_grid["dem"] = np.ravel(processed_grid.z, order="F")

    return processed_grid


def generate_gif_maps(args):
    """
    Main function.
    """

    # Save original map:
    counter = 0

    if args.gen_from_tiles:
        args.sample_from = None

    if args.sample_from is not None:
        _, _, scene = generate_map(specific_map=args.sample_from)
        grid = apply_texture_and_bottom(scene)
        grid.plot(
            cmap="summer",
            show_scalar_bar=False,
            screenshot=os.path.join(args.folder_path, "screenshot", str(counter) + ".png"),
            off_screen=True,
        )

    else:
        gen_setup(args.max_height)

    # Saving maps with increasing size
    for width in range(args.min_width, args.max_width, args.interval_width):
        for height in range(width, width + args.interval_width + 1, args.interval_width):

            counter += 1
            _, _, scene = generate_map(
                width=width,
                height=height,
                periodic_output=args.periodic_output,
                sample_from=args.sample_from,
                seed=args.seed,
                max_height=args.max_height,
                N=args.N,
                periodic_input=args.periodic_input,
                ground=args.ground,
                symmetry=args.symmetry,
            )

            grid = apply_texture_and_bottom(scene)
            grid.plot(
                cmap="summer",
                show_scalar_bar=False,
                screenshot=os.path.join(args.folder_path, "screenshot", str(counter) + ".png"),
                off_screen=True,
            )

    return counter


def create_gif(folder_path, counter):
    """
    Create the gif.
    """

    # build gif
    with imageio.get_writer(os.path.join(folder_path, "maps.gif"), mode="I") as writer:
        for i in range(counter):
            filename = os.path.join(folder_path, str(i + 1) + ".png")
            image = imageio.v2.imread(filename)
            writer.append_data(image)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Check generate_env for more information about the arguments where
    # `help`` is not provided
    parser.add_argument("--periodic_output", type=bool, default=True)
    parser.add_argument("--periodic_input", type=bool, default=True)
    parser.add_argument("--ground", type=bool, default=False)
    parser.add_argument(
        "--gen_from_tiles",
        type=bool,
        default=False,
        help="If true, generate maps from tiles instead of using \
                        a pre-built map",
    )

    parser.add_argument("--min_width", type=int, default=5, help="Minimum width of maps generated for the gif.")
    parser.add_argument("--max_width", type=int, default=21, help="Maximum width of maps generated for the gif.")
    parser.add_argument("--interval_width", type=int, default=2, help="Step when increasing size of maps.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max_height", type=int, default=8)
    parser.add_argument("--symmetry", type=int, default=1)
    parser.add_argument("--N", type=int, default=2)

    parser.add_argument("--sample_from", type=str, default="example_map_01")

    args = parser.parse_args()

    # Generate example map if not generated already
    if args.sample_from is None:
        gen_setup(args.max_height)

    else:
        name = args.sample_from
        map_2d = create_2d_map(name)

    # Create screenshot folder if it doesn't exist
    if not os.path.exists(os.path.join(args.folder_path, "screenshot")):
        os.makedirs(os.path.join(args.folder_path, "screenshot"))

    counter = generate_gif_maps(args)
    create_gif(os.path.join(args.folder_path, "screenshot"), counter)
