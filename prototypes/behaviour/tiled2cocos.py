#!/usr/bin/env python
# 
# Copyright (c) 2009 Maik Gosenshuis
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright 
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of tiled2cocos nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""
Converts .tmx files generated by the generic WYSIWYG map editor Tiled
(http://www.mapeditor.org) into a corresponding MapLayer to be used in cocos2d.

Currently, this deserializer only supports orthogonal (rectangle) maps.
You can deserialize a map by passing a valid .tmx file path to the
load_map() method in this module.

This module has been tested with Tiled 0.7.2, cocos2d 0.3.0 and pyglet 1.1.3.

You can find more information on this module on its Bitbucket repository:
http://bitbucket.org/maikg/tiled2cocos/
"""


import pyglet.image
import cocos.tiles
import xml.dom.minidom
import os.path
import base64
import gzip
from cStringIO import StringIO
from array import array


__all__ = ['load_map', 'MapException']


class MapException(Exception):
    """Indicates a problem with the map's data, not with its mark-up."""
    pass


def load_map(filename):
    """Creates a cocos2d RectMapLayer object based on the Tiled .tmx file."""
    doc = xml.dom.minidom.parse(filename)

    map_node = doc.documentElement
    
    # Only support orthogonal (rectangle) oriented maps for now.
    if map_node.getAttribute('orientation') <> 'orthogonal':
        raise MapException('tiled2cocos only supports orthogonal maps for now.')

    tile_width = int(map_node.getAttribute('tilewidth'))
    tile_height = int(map_node.getAttribute('tileheight'))

    # We want to find the absolute path to the directory containing our XML file
    # so we can create paths relative to the XML file, not from the current
    # working directory.
    root_dir = os.path.dirname(os.path.abspath(filename))
    
    # Load all the available tiles into a dictionary, where the keys are gids
    # and the values are cocos Tile objects.
    tiles = load_tilesets(map_node, root_dir)
    
    gid_matrix = create_gid_matrix(map_node)

    cells = []
    for i, column in enumerate(gid_matrix):
        col = []
        for j, gid in enumerate(column):
            col.append(cocos.tiles.RectCell(i, j, tile_width, tile_height, {}, tiles[gid]))
        cells.append(col)

    rect_map = cocos.tiles.RectMapLayer('map', tile_width, tile_height, cells)

    # Properties on maps are not supported by default, but we can set properties as
    # an attribute ourselves.
    rect_map.properties = load_properties(map_node)

    return rect_map


def load_tilesets(map_node, root_dir):
    """Creates the cocos2d TileSet objects from .tmx tileset nodes."""
    tileset_nodes = map_node.getElementsByTagName('tileset')
    tiles = {}
    for tileset_node in tileset_nodes:
        if tileset_node.hasAttribute('source'):
            # The tileset links to an external tileset file, so we load that file
            # and replace tileset_node with the root element of that file, which
            # is also a tileset node with the same structure.
            tileset_filename = tileset_node.getAttribute('source')
            tileset_doc = xml.dom.minidom.parse(os.path.join(root_dir, tileset_filename))
            real_node = tileset_doc.documentElement
            
            # The firstgid attribute in the external tileset file is meaningless,
            # since there is no way for it to be relative to the other tilesets in
            # in the map file.
            real_node.setAttribute('firstgid', tileset_node.getAttribute('firstgid'))
        else:
            real_node = tileset_node

        tiles.update(load_tiles(real_node, root_dir))
    
    return tiles


def load_tiles(tileset_node, root_dir):
    """Loads the tiles from one tileset."""
    tiles = {}

    tile_width = int(tileset_node.getAttribute('tilewidth'))
    tile_height = int(tileset_node.getAttribute('tileheight'))
    spacing = int(try_attribute(tileset_node, 'spacing', 0))
    
    # Margin support appears to be broken in Tiled (0.7.2), so it is disabled
    # for now.
    margin = 0

    image_atlas_file = get_first(tileset_node, 'image').getAttribute('source')
    image_atlas = pyglet.image.load(os.path.join(root_dir, image_atlas_file))

    # Load all tile properties for this tileset in one batch, instead of querying
    # them separately.
    tile_properties = load_tile_properties(tileset_node)

    gid = int(tileset_node.getAttribute('firstgid'))
    
    # Start at the top left corner of the image.
    y = image_atlas.height - tile_height
    while y >= 0:
        x = 0
        while x + tile_width <= image_atlas.width:
            # Extract the relevant portion from the atlas image.
            tile_image = image_atlas.get_region(x, y, tile_width, tile_height)
            properties = tile_properties.get(gid, {})
            tiles[gid] = cocos.tiles.Tile(gid, properties, tile_image)
            
            gid += 1
            x += tile_width + spacing
        y -= tile_height + spacing

    return tiles


def load_tile_properties(tileset_node):
    """Fetches properties for tiles from a tileset. Returns a dictionary, where the keys are
    the tile IDs."""
    first_gid = int(tileset_node.getAttribute('firstgid'))
    tile_nodes = tileset_node.getElementsByTagName('tile')

    properties = {}

    for tile_node in tile_nodes:
        # The id attribute specifies a unique id for a tile PER TILESET. This is different
        # from the 'gid' attribute.
        gid = int(tile_node.getAttribute('id')) + first_gid
        properties[gid] = load_properties(tile_node)

    return properties


def load_properties(node):
    """Loads properties on a .tmx node into a dictionary. Checks for existence of
    a properties node. Returns an empty dictionary if no properties are available."""
    properties = {}

    if has_child(node, 'properties'):
        property_nodes = get_first(node, 'properties').getElementsByTagName('property')

        for property_node in property_nodes:
            name = property_node.getAttribute('name')
            value = property_node.getAttribute('value')
            properties[name] = value

    return properties


def create_gid_matrix(map_node):
    """Creates a column ordered bottom-up, left-right gid matrix by iterating over all
    the layers in the map file, overwriting all positions in the gid matrix for all non-empty
    tiles in each layer. This method also enforces that all tile spots in the final gid matrix
    are occupied. It raises a MapException if any tile locations are not occupied, based on
    the width and height of the map."""
    width = int(map_node.getAttribute('width'))
    height = int(map_node.getAttribute('height'))

    gid_matrix = create_empty_gid_matrix(width, height)

    layer_nodes = map_node.getElementsByTagName('layer')

    for layer_node in layer_nodes:        
        data_node = get_first(layer_node, 'data')
        
        gids = get_gids(data_node)
        
        for tile_index, gid in enumerate(gids):
            # Only overwrite the current tile in this position if it contains
            # a non-empty tile.
            if gid > 0:
                gid_matrix[tile_index // width][tile_index % width] = gid

    if any([min(row) <= 0 for row in gid_matrix]):
        raise MapException('All tile locations should be occupied.')

    return rotate_matrix_ccw(gid_matrix)


def create_empty_gid_matrix(width, height):
    """Creates a matrix of the given size initialized with all zeroes."""
    return [[0] * width for row_index in range(height)]


def get_gids(data_node):
    """Returns all gids for the specified data node. Gids are returned in a left-right,
    top-bottom order, as a sequence of ints. Takes care of decoding and decompression if
    necessary."""    
    if try_attribute(data_node, 'encoding') == 'base64':
        data = base64.b64decode(get_text_contents(data_node))
        
        # Tiled can only do gzip compression when base64 encoding is on.
        if try_attribute(data_node, 'compression') == 'gzip':
            data = decompress_data(data)
        
        return array('L', data)
    else:
        # No encoding or compression.        
        tile_nodes = data_node.getElementsByTagName('tile')
        
        gids = []
        for tile_node in tile_nodes:
            gids.append(int(tile_node.getAttribute('gid')))
            
        return gids


def decompress_data(data):
    """Decompresses a string of gzipped layer data."""
    data_buffer = StringIO(data)
    gzip_file = gzip.GzipFile('', 'rb', 9, data_buffer)
    data = gzip_file.read()
    gzip_file.close()
    data_buffer.close()
    
    return data


def rotate_matrix_ccw(matrix):
    """Rotates a matrix 90 degrees counter-clockwise. This is used to turn tiled's left-right,
    top-bottom order into cocos' column based bottom-up, left-right order."""
    result = []
    for row in zip(*matrix):
        row = list(row)
        row.reverse()
        result.append(row)
    return result


def get_text_contents(node, preserve_whitespace=False):
    """Returns the text contents for a particular node. By default discards
    leading and trailing whitespace."""
    result = ''.join([node.data for node in node.childNodes if node.nodeType == node.TEXT_NODE])
    
    if not preserve_whitespace:
        result = result.strip()
    
    return result


def get_first(parent, tag_name):
    """Returns the parent's first child tag matching the tag name."""
    return parent.getElementsByTagName(tag_name)[0]


def try_attribute(node, attribute_name, default=None):
    """Tries to get an attribute from the supplied node. Returns the default
    value if the attribute is unavailable."""
    if node.hasAttribute(attribute_name):
        return node.getAttribute(attribute_name)
    
    return default


def has_child(node, child_tag_name):
    """Determines if the node has at least one child with the specified tag name."""
    return len(node.getElementsByTagName(child_tag_name)) > 0
