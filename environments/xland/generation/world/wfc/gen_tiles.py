"""
Generate tiles for debugging purposes, and for generating maps on the prototype.
"""

from PIL import Image
import numpy as np
from shutil import rmtree
import os


def generate_xml(width, height, 
                names_xml, neighbors_xml, 
                tile_size, tiles_folder, 
                gen_folder):
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
        f.write('<set size="{}" unique="True">\n'.format(tile_size))

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
        f.write('\t<simpletiled name="tiles" width="{}" height="{}" periodic="True"/>\n'.format(width, height))
        f.write('</samples>')

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

def add_constraint(xml_str, left, right, left_or=0, right_or=0):
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

def generate_tiles(width=9,
                  height=9,
                  weights=None,
                  max_height=8,
                  gen_folder='.gen_files',
                  tile_size=2,
                  save=True):
    """
    Generate tiles for the procedural generation.
    NOTE: So far, we are using these values to get used to how to use the algorithm.

    Args:
        weights: weights for each of the levels of height. If none, defaults for a linear decay between [10, 0.2]
        max_height: must be a power of 2 and less than 256 for now.
        gen_folder: folder where generation elements are saved.
        tile_size: size of the tiles.
        save: if True, tiles are saved in gen_folder/tiles.
            TODO: Optionally, we could pass directly the generated map instead of saving
            intermediary tiles.

    Returns:
        None
    """

    # TODO: which should be default weights?
    if weights is None:
        weights = np.linspace(10.0, 0.2, max_height)

    print("Generating tiles with max height: {}".format(max_height))

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
        
        # TODO: there's a bug on this
        rmtree(tiles_folder)

    # Recreate the tiles folder
    os.makedirs(tiles_folder)
    
    print("Saving tiles to {}".format(tiles_folder))

    # Step for the height (which is represented by the intensity of the color)
    color_step = 256 // max_height
    names_xml = ''
    neighbors_xml = ''
    tiles = []
    plain_tile_names = ['{}0'.format(h) for h in range(max_height)]

    # Generate tiles
    for h in range(max_height):
        color = h * color_step
        color_above = (h + 1) * color_step

        # Generate plain tile
        tile = Image.new('RGB', size=(tile_size, tile_size), color=(color, color, color))
        tiles.append(tile)

        # TODO: should we always save the tiles?
        # Saving the tiles could be helpful to resume training, etc
        if save:
            tile.save(os.path.join(tiles_folder, plain_tile_names[h] + ".png"))
            
            # Symmetry of a certain letter means that it has the sames symmetric properties
            # as the letter
            names_xml = add_tile_name(names_xml, plain_tile_names[h], weights[h], symmetry="X")
            
            # Add plain tiles as neighbors
            for hh in range(max_height):
                neighbors_xml = add_constraint(neighbors_xml, plain_tile_names[h], plain_tile_names[hh])

        # If i == max_height - 1, then we don't add more ramps
        if h < max_height - 1:

            # NOTE: One improvement here is to start using the argument `symmetry` on the
            # xml file instead of hardcoding it here.
            # Generation of ramp tiles:
            # Here we only generate from bottom to top, right to left, left to right
            # and top to bottom, in this order
            for i in range(0, 2):
                for ax in range(0, 2):

                    tile = Image.new('RGB', size=(tile_size, tile_size), color=(color_above, color_above, color_above))
                    tile_np = np.array(tile)
                    
                    begin = i * tile_size // 2
                    end = (i+1) * tile_size // 2

                    if ax == 0:
                        tile_np[begin:end,:,:] = color
                    else:
                        tile_np[:,begin:end,:] = color
    
                    tile_np = np.reshape(tile_np, (tile_size * tile_size, 3))
                    tile.putdata([tuple(tile_np[i]) for i in range(tile_size * tile_size)])
                    tiles.append(tile)

                    if save:
                        next_ramp_name = '{}{}'.format(h + 1, i * 2 + ax + 1)
                        ramp_name = '{}{}'.format(h, i * 2 + ax + 1)

                        tile.save(os.path.join(tiles_folder, ramp_name + ".png"))
                        names_xml = add_tile_name(names_xml, ramp_name, weights[h])

                        # We add neighbors
                        # Notice that we have to add orientation
                        # The tiles are rotate clockwise as i * 2 + ax increases
                        # And we add a rotation to fix that and keep the ramps in the right place
                        ramp_or = i * 2 + ax
                        neighbors_xml = add_constraint(neighbors_xml, ramp_name, plain_tile_names[h], ramp_or, 0)
                        neighbors_xml = add_constraint(neighbors_xml, plain_tile_names[h+1], ramp_name, 0, ramp_or)

                        # Adding ramp to going upwards
                        # TODO: review this
                        if h < max_height - 2:
                            neighbors_xml = add_constraint(neighbors_xml, next_ramp_name, ramp_name, ramp_or, ramp_or)



    # Create xml file
    if save:
        generate_xml(width, height, names_xml, neighbors_xml, tile_size, tiles_folder, gen_folder)
    
    print("Done generating tiles.")


if __name__ == '__main__':
    generate_tiles(width=10, height=10, max_height=5, tile_size=16, save=True)
