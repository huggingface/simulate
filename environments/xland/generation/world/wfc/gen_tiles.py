"""
Generate tiles for debugging purposes, and for generating maps on the prototype.
"""

from PIL import Image
import numpy as np
from shutil import rmtree
import os


def generate_xml(names_xml, neighbors_xml, tiles_folder, gen_folder):
    """
    Generate xml file for debugging purposes.
    
    Constraints: ramps must start on a certain height and
    go to the next height of the map or go to the same ramp.

    Args:
        names_xml: names of tiles
        neighbors_xml: which tiles can be neighbors
        tiles_folder: folder where tiles are saved.

    Returns:
        None
    """

    xml_file = os.path.join(tiles_folder, 'data.xml')

    # First generate the file with names and neighbors
    with open(xml_file, 'w') as f:
        f.write('<set size="48" unique="True">\n')

        # Write tile names
        f.write('\t<tiles>\n')
        f.write(names_xml)
        f.write('\t</tiles>\n')

        # Write neighbors
        f.write('\t<neighbors>\n')
        f.write(neighbors_xml)
        f.write('\t</neighbors>\n')

        f.write('</set>')

    # Now, the samples file 
    # TODO: might not be necessary to create two different files
    sample_xml_file = os.path.join(gen_folder, 'samples.xml')
    with open(sample_xml_file, 'w') as f:
        f.write('<samples>\n')
        f.write('\t<overlapping name="tiles" width="15" height="15" periodic="False" limit="15"/>\n')
        f.write('</samples>')

def add_tile_name(xml_str, tile_name):
    """
    Add the name of the tile to the xml string.

    Args:
        xml_str: xml string to be modified.
        tile_name: name of the tile.

    Returns:
        xml_str: xml string with the tile name.
    """
    return xml_str + '\t\t<tile_name>{}</tile_name>\n'.format(tile_name)

def add_constraint(xml_str, left, right):
    """
    Add a constraint to the xml string.

    Args:
        xml_str: xml string to be modified.
        left: left side of the constraint.
        right: right side of the constraint.

    Returns:
        xml_str: xml string with the constraint.
    """
    return xml_str + '\t\t<neighbor left="{}" right="{}"/>\n'.format(left, right)

def img_from_tiles():
    raise NotImplementedError

def generate_tiles(max_height=8,
                  gen_folder='.gen_files',
                  tile_size=2,
                  save=True):
    """
    Generate tiles for the procedural generation.
    NOTE: So far, we are using these values to get used to how to use the algorithm.

    Args:
        max_height: must be a power of 2 and less than 256 for now.
        gen_folder: folder where generation elements are saved.
        tile_size: size of the tiles.
        save: if True, tiles are saved in gen_folder/tiles.
            TODO: Optionally, we could pass directly the generated map instead of saving
            intermediary tiles.

    Returns:
        None
    """

    print("Generating tiles with max height: {}".format(max_height))

    # TODO: increase frequency of certain tiles if this impacts the algorithm

    # Create the folder if it doesn't exist.
    if not os.path.exists(gen_folder):
        os.makedirs(gen_folder)
    
    # Create the tiles folder
    tiles_folder = os.path.join(gen_folder, 'tiles')

    if os.path.exists(tiles_folder):
        print("Tiles folder already exists. Continuing will overwrite current tiles. \
            Do you wish to continue? (y/n)")
        
        answer = input()
        if answer != 'y':
            return
        
        rmtree(tiles_folder)

    # Recreate the tiles folder
    os.makedirs(tiles_folder)
    
    print("Saving tiles to {}".format(tiles_folder))

    # Step for the height (which is represented by the intensity of the color)
    color_step = 256 // max_height
    names_xml = ''
    neighbors_xml = ''
    tiles = []

    # Generate tiles
    for h in range(max_height):
        color = 255 - (h + 1) * color_step
        color_above = 255 - (h + 2) * color_step

        # Generate plain tile
        tile = Image.new('L', size=(tile_size, tile_size), color=(color))
        tiles.append(tile)

        # TODO: should we always save the tiles?
        # Saving the tiles could be helpful to resume training, etc
        if save:
            name = '{}0.png'.format(h)
            tile.save(os.path.join(tiles_folder, name))
            names_xml = add_tile_name(names_xml, name)

        # TODO: generate ramp tiles to the next height
        # If i == max_height - 1, then we don't add more ramps
        if h < max_height - 1:
            name_above = '{}0.png'.format(h + 1)

            # NOTE: One improvement here is to start using the argument `symmetry` on the
            # xml file instead of hardcoding it here.
            # Generation of ramp tiles:
            # Here we only generate from bottom to top, right to left, left to right
            # and top to bottom, in this order
            for i in range(0, 2):
                for ax in range(0, 2):

                    tile = Image.new('L', size=(tile_size, tile_size), color=(color_above))
                    tile_np = np.array(tile)
                    np.put_along_axis(tile_np, np.reshape(np.tile(i, tile_size), (1, tile_size)), color, axis=ax)
                    tile.putdata(tile_np.flatten())
                    tiles.append(tile)

                    if save:
                        ramp_name = '{}{}.png'.format(h, i * 2 + ax + 1)
                        tile.save(os.path.join(tiles_folder, ramp_name))
                        names_xml = add_tile_name(names_xml, ramp_name)
                        neighbors_xml = add_constraint(neighbors_xml, name, ramp_name)
                        neighbors_xml = add_constraint(neighbors_xml, ramp_name, name_above)



    # Create xml file
    if save:
        generate_xml(names_xml, neighbors_xml, tiles_folder, gen_folder)

    # Tiles would be used to make a visualization image
    # TODO: needs to implement img_from_tiles
    # img_from_tiles(tiles)
    
    print("Done generating tiles.")


if __name__ == '__main__':
    generate_tiles(save=True)
