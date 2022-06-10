"""
Generate tiles for debugging purposes, and for generating maps on the prototype.
"""

import os

import numpy as np
from PIL import Image


def generate_xml(names_xml, neighbors_xml, tiles_folder, gen_folder):
    """
    Generate xml file for debugging purposes.

    Constraints: ramps must start on a certain height and
    go to the next height of the map or go to the same ramp.

    Args:
        names_xml: names of tiles
        neighbors_xml: which tiles can be neighbors
        tiles_folder: folder where tiles are saved.
        gen_folder: folder where generation files and maps are saved.

    Returns:
        None
    """

    xml_file = os.path.join(tiles_folder, "data.xml")

    # First generate the file with names and neighbors
    with open(xml_file, "w") as f:
        f.write('<set size="1" unique="True">\n')

        # Write tile names
        f.write("\t<tiles>\n")
        f.write(names_xml)
        f.write("\t</tiles>\n")

        # Write neighbors
        f.write("\t<neighbors>\n")
        f.write(neighbors_xml)
        f.write("\t</neighbors>\n")

        f.write("</set>")


def add_tile_name(xml_str, tile_name, weight, symmetry="L"):
    """
    Add the name of the tile to the xml string.

    Args:
        xml_str: xml string to be modified.
        tile_name: name of the tile.

    Returns:
        xml_str: xml string with the tile name.
    """
    return xml_str + '\t\t<tile name="{}" symmetry="{}" weight="{}"/>\n'.format(tile_name, symmetry, weight)


def add_neighbor(xml_str, left, right, left_or=0, right_or=0):
    """
    Add a neighbors to the xml string.

    These neighbors show which constraints need to be followed by the algorithm.

    Args:
        xml_str: xml string to be modified.
        left: left side of the constraint.
        right: right side of the constraint.
        left_or: orientation of left tile.
        right_or: orientation of right tile

    Returns:
        xml_str: xml string with the constraint.
    """
    return xml_str + '\t\t<neighbor left="{} {}" right="{} {}"/>\n'.format(left, left_or, right, right_or)


def img_from_tiles():
    """
    Transform tiles into an unique image for tile visualization.
    """
    raise NotImplementedError


def generate_tiles(max_height=8, weights=None, gen_folder=".gen_files", double_ramp=False):
    """
    Generate tiles for the procedural generation.
    NOTE: So far, we are using these values to get used to how to use the algorithm.

    Args:
        max_height: can be any integer between 1 and 256 (and it's advisable to use a power of 2, to avoid
            approximation errors).
        weights: weights for each of the levels of height. If none, defaults for a linear decay between [10, 0.2]
        gen_folder: folder where generation elements are saved.
        double_ramp: whether double ramps should be allowed or not.

    Returns:
        None
    """

    # TODO: which should be default weights?
    if weights is None:
        weights = np.exp(np.linspace(1.0, -4.0, max_height))

    ramp_weights = [0.1] * max_height

    print("Generating tiles with max height: {}".format(max_height))

    tiles_folder = os.path.join(gen_folder, "tiles")
    print("Saving tiles to {}".format(tiles_folder))

    # Step for the height (which is represented by the intensity of the color)
    names_xml = ""
    neighbors_xml = ""
    tiles = []
    plain_tile_names = ["{}0".format(h) for h in range(max_height)]

    # Generate tiles
    for h in range(max_height):

        # Generate plain tile
        tile = Image.new("RGB", size=(1,1), color=(h, 0, 0))
        tiles.append(tile)

        # Saving plain tiles
        tile.save(os.path.join(tiles_folder, plain_tile_names[h] + ".png"))

        # Symmetry of a certain letter means that it has the sames symmetric properties
        # as the letter
        names_xml = add_tile_name(names_xml, plain_tile_names[h], weights[h], symmetry="X")
        neighbors_xml = add_neighbor(neighbors_xml, plain_tile_names[h], plain_tile_names[h])
        
        if h < max_height - 2:
            neighbors_xml = add_neighbor(neighbors_xml, plain_tile_names[h], plain_tile_names[h + 1])

        # If i == max_height - 1, then we don't add more ramps
        if h < max_height - 1:

            # NOTE: One improvement here is to start using the argument `symmetry` on the
            # xml file instead of hardcoding it here.
            # Generation of ramp tiles:
            # Here we only generate from bottom to top, right to left, left to right
            # and top to bottom, in this order
            for i in range(0, 2):
                for ax in range(0, 2):
                    # Ramp orientation (more details down here)
                    ramp_or = i * 2 + ax

                    tile = Image.new("RGB", size=(1, 1), color=(h, ramp_or + 1, 0))
                    tile_np = np.array(tile)

                    tile_np = np.ravel(tile_np)
                    tile.putdata([tuple(tile_np)])
                    tiles.append(tile)

                    # Save tiles
                    next_ramp_name = "{}{}".format(h + 1, ramp_or + 1)
                    ramp_name = "{}{}".format(h, ramp_or + 1)

                    tile.save(os.path.join(tiles_folder, ramp_name + ".png"))
                    names_xml = add_tile_name(names_xml, ramp_name, ramp_weights[h], symmetry="L")

                    # We add neighbors
                    # Notice that we have to add orientation
                    # The tiles are rotate clockwise as i * 2 + ax increases
                    # And we add a rotation to fix that and keep the ramps in the right place
                    neighbors_xml = add_neighbor(neighbors_xml, ramp_name, plain_tile_names[h], ramp_or, 0)
                    neighbors_xml = add_neighbor(neighbors_xml, plain_tile_names[h + 1], ramp_name, 0, ramp_or)

                    # Adding ramp to going upwards
                    if h < max_height - 2 and double_ramp:
                        neighbors_xml = add_neighbor(neighbors_xml, next_ramp_name, ramp_name, ramp_or, ramp_or)

    # Create xml file
    generate_xml(names_xml, neighbors_xml, tiles_folder, gen_folder)

    print("Done generating tiles.")
