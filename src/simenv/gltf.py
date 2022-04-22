# Copyright 2022 The HuggingFace Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
""" Load a GLTF file in a Scene."""
import numpy as np

from .gltflib import GLTF


def load_gltf(file_path):
    gltf = GLTF.load(file_path, load_file_resources=True)


def _read_buffers(header, buffers, mesh_kwargs, ignore_broken=False, merge_primitives=False, resolver=None):
    """
    Given binary data and a layout return the
    kwargs to create a scene object.

    Parameters
    -----------
    header : dict
      With GLTF keys
    buffers : list of bytes
      Stored data
    mesh_kwargs : dict
      To be passed to the mesh constructor.
    ignore_broken : bool
      If there is a mesh we can't load and this
      is True don't raise an exception but return
      a partial result
    merge_primitives : bool
      If true, combine primitives into a single mesh.
    resolver : trimesh.resolvers.Resolver
      Resolver to load referenced assets

    Returns
    -----------
    kwargs : dict
      Can be passed to load_kwargs for a trimesh.Scene
    """

    if "bufferViews" in gltf.model:
        # split buffer data into buffer views
        views = [None] * len(header["bufferViews"])
        for i, view in enumerate(header["bufferViews"]):
            if "byteOffset" in view:
                start = view["byteOffset"]
            else:
                start = 0
            end = start + view["byteLength"]
            views[i] = buffers[view["buffer"]][start:end]

            assert len(views[i]) == view["byteLength"]

        # load data from buffers into numpy arrays
        # using the layout described by accessors
        access = [None] * len(header["accessors"])
        for index, a in enumerate(header["accessors"]):
            # number of items
            count = a["count"]
            # what is the datatype
            dtype = _dtypes[a["componentType"]]
            # basically how many columns
            per_item = _shapes[a["type"]]
            # use reported count to generate shape
            shape = np.append(count, per_item)
            # number of items when flattened
            # i.e. a (4, 4) MAT4 has 16
            per_count = np.abs(np.product(per_item))
            if "bufferView" in a:
                # data was stored in a buffer view so get raw bytes
                data = views[a["bufferView"]]
                # is the accessor offset in a buffer
                if "byteOffset" in a:
                    start = a["byteOffset"]
                else:
                    # otherwise assume we start at first byte
                    start = 0
                # length is the number of bytes per item times total
                length = np.dtype(dtype).itemsize * count * per_count
                # load the bytes data into correct dtype and shape

                access[index] = np.frombuffer(data[start : start + length], dtype=dtype).reshape(shape)

            else:
                # a "sparse" accessor should be initialized as zeros
                access[index] = np.zeros(count * per_count, dtype=dtype).reshape(shape)

        # load images and textures into material objects
        materials = _parse_materials(header, views=views, resolver=resolver)

    mesh_prim = collections.defaultdict(list)
    # load data from accessors into Trimesh objects
    meshes = collections.OrderedDict()

    names_original = collections.defaultdict(list)

    for index, m in enumerate(header.get("meshes", [])):

        try:
            # GLTF spec indicates implicit units are meters
            metadata = {"units": "meters"}
            # try to load all mesh metadata
            if isinstance(m.get("extras"), dict):
                metadata.update(m["extras"])

            for j, p in enumerate(m["primitives"]):
                # if we don't have a triangular mesh continue
                # if not specified assume it is a mesh
                kwargs = {"metadata": {}, "process": False}
                kwargs.update(mesh_kwargs)
                kwargs["metadata"].update(metadata)

                # i.e. GL_LINES, GL_TRIANGLES, etc
                mode = p.get("mode")
                # colors, normals, etc
                attr = p["attributes"]
                # create a unique mesh name per- primitive
                name = m.get("name", "GLTF")
                names_original[index].append(name)
                # make name unique across multiple meshes
                if name in meshes:
                    name += "_" + util.unique_id(length=5)
                    assert name not in meshes
                if mode == _GL_LINES:
                    # load GL_LINES into a Path object
                    from ..path.entities import Line

                    kwargs["vertices"] = access[attr["POSITION"]]
                    kwargs["entities"] = [Line(points=np.arange(len(kwargs["vertices"])))]
                elif mode == _GL_POINTS:
                    kwargs["vertices"] = access[attr["POSITION"]]
                elif mode is None or mode in (_GL_TRIANGLES, _GL_STRIP):
                    if mode is None:
                        # some people skip mode since GL_TRIANGLES
                        # is apparently the de-facto default
                        log.warning("primitive has no mode! trying GL_TRIANGLES?")
                        # get vertices from accessors
                    kwargs["vertices"] = access[attr["POSITION"]]
                    # get faces from accessors
                    if "indices" in p:
                        if mode == _GL_STRIP:
                            # this is triangle strips
                            flat = access[p["indices"]].reshape(-1)
                            kwargs["faces"] = util.triangle_strips_to_faces([flat])
                        else:
                            kwargs["faces"] = access[p["indices"]].reshape((-1, 3))

                    else:
                        # indices are apparently optional and we are supposed to
                        # do the same thing as webGL drawArrays?
                        kwargs["faces"] = np.arange(len(kwargs["vertices"]), dtype=np.int64).reshape((-1, 3))
                    if "NORMAL" in attr:
                        # vertex normals are specified
                        kwargs["vertex_normals"] = access[attr["NORMAL"]]
                        # do we have UV coordinates
                    visuals = None
                    if "material" in p:
                        if materials is None:
                            log.warning("no materials! `pip install pillow`")
                        else:
                            uv = None
                            if "TEXCOORD_0" in attr:
                                # flip UV's top- bottom to move origin to lower-left:
                                # https://github.com/KhronosGroup/glTF/issues/1021
                                uv = access[attr["TEXCOORD_0"]].copy()
                                uv[:, 1] = 1.0 - uv[:, 1]
                                # create a texture visual
                            visuals = visual.texture.TextureVisuals(uv=uv, material=materials[p["material"]])

                    if "COLOR_0" in attr:
                        try:
                            # try to load vertex colors from the accessors
                            colors = access[attr["COLOR_0"]]
                            if len(colors) == len(kwargs["vertices"]):
                                if visuals is None:
                                    # just pass to mesh as vertex color
                                    kwargs["vertex_colors"] = colors
                                else:
                                    # we ALSO have texture so save as vertex attribute
                                    visuals.vertex_attributes["color"] = colors
                        except BaseException:
                            # survive failed colors
                            log.debug("failed to load colors", exc_info=True)
                    if visuals is not None:
                        kwargs["visual"] = visuals

                    # By default the created mesh is not from primitive,
                    # in case it is the value will be updated
                    # each primitive gets it's own Trimesh object
                    if len(m["primitives"]) > 1:
                        kwargs["metadata"]["from_gltf_primitive"] = True
                        name += "_{}".format(j)
                    else:
                        kwargs["metadata"]["from_gltf_primitive"] = False

                    # custom attributes starting with a `_`
                    custom = {a: access[attr[a]] for a in attr.keys() if a.startswith("_")}
                    if len(custom) > 0:
                        kwargs["vertex_attributes"] = custom
                else:
                    log.warning("skipping primitive with mode %s!", mode)
                    continue
                meshes[name] = kwargs
                mesh_prim[index].append(name)
        except BaseException as E:
            if ignore_broken:
                log.debug("failed to load mesh", exc_info=True),
            else:
                raise E
    # sometimes GLTF "meshes" come with multiple "primitives"
    # by default we return one Trimesh object per "primitive"
    # but if merge_primitives is True we combine the primitives
    # for the "mesh" into a single Trimesh object
    if merge_primitives:
        # if we are only returning one Trimesh object
        # replace `mesh_prim` with updated values
        mesh_prim_replace = dict()
        mesh_pop = []
        for mesh_index, names in mesh_prim.items():
            if len(names) <= 1:
                mesh_prim_replace[mesh_index] = names
                continue
            name = names_original[mesh_index][0]
            if name in meshes:
                name = name + "_" + str(np.random.random())[2:12]
            # remove the other meshes after we're done looping
            mesh_pop.extend(names[:])
            # collect the meshes
            # TODO : use mesh concatenation with texture support
            current = [meshes[n] for n in names]
            v_seq = [p["vertices"] for p in current]
            f_seq = [p["faces"] for p in current]
            v, f = util.append_faces(v_seq, f_seq)
            materials = [p["visual"].material for p in current]
            face_materials = []
            for i, p in enumerate(current):
                face_materials += [i] * len(p["faces"])
            visuals = visual.texture.TextureVisuals(
                material=visual.material.MultiMaterial(materials=materials), face_materials=face_materials
            )
            if "metadata" in meshes[names[0]]:
                metadata = meshes[names[0]]["metadata"]
            else:
                metadata = {}
            meshes[name] = {"vertices": v, "faces": f, "visual": visuals, "metadata": metadata, "process": False}
            mesh_prim_replace[mesh_index] = [name]
        # avoid altering inside loop
        mesh_prim = mesh_prim_replace
        # remove outdated meshes
        [meshes.pop(p, None) for p in mesh_pop]

    # make it easier to reference nodes
    nodes = header["nodes"]
    # nodes are referenced by index
    # save their string names if they have one
    # node index (int) : name (str)
    names = {}
    for i, n in enumerate(nodes):
        if "name" in n:
            if n["name"] in names.values():
                names[i] = n["name"] + "_{}".format(util.unique_id())
            else:
                names[i] = n["name"]
        else:
            names[i] = str(i)

    # make sure we have a unique base frame name
    base_frame = "world"
    if base_frame in names:
        base_frame = str(int(np.random.random() * 1e10))
    names[base_frame] = base_frame

    # visited, kwargs for scene.graph.update
    graph = collections.deque()
    # unvisited, pairs of node indexes
    queue = collections.deque()

    if "scene" in header:
        # specify the index of scenes if specified
        scene_index = header["scene"]
    else:
        # otherwise just use the first index
        scene_index = 0

    # start the traversal from the base frame to the roots
    for root in header["scenes"][scene_index]["nodes"]:
        # add transform from base frame to these root nodes
        queue.append([base_frame, root])

    # go through the nodes tree to populate
    # kwargs for scene graph loader
    while len(queue) > 0:
        # (int, int) pair of node indexes
        a, b = queue.pop()

        # dict of child node
        # parent = nodes[a]
        child = nodes[b]
        # add edges of children to be processed
        if "children" in child:
            queue.extend([[b, i] for i in child["children"]])

        # kwargs to be passed to scene.graph.update
        kwargs = {"frame_from": names[a], "frame_to": names[b]}

        # grab matrix from child
        # parent -> child relationships have matrix stored in child
        # for the transform from parent to child
        if "matrix" in child:
            kwargs["matrix"] = np.array(child["matrix"], dtype=np.float64).reshape((4, 4)).T
        else:
            # if no matrix set identity
            kwargs["matrix"] = np.eye(4)

        # Now apply keyword translations
        # GLTF applies these in order: T * R * S
        if "translation" in child:
            kwargs["matrix"] = np.dot(kwargs["matrix"], transformations.translation_matrix(child["translation"]))
        if "rotation" in child:
            # GLTF rotations are stored as (4,) XYZW unit quaternions
            # we need to re- order to our quaternion style, WXYZ
            quat = np.reshape(child["rotation"], 4)[[3, 0, 1, 2]]
            # add the rotation to the matrix
            kwargs["matrix"] = np.dot(kwargs["matrix"], transformations.quaternion_matrix(quat))
        if "scale" in child:
            # add scale to the matrix
            kwargs["matrix"] = np.dot(kwargs["matrix"], np.diag(np.concatenate((child["scale"], [1.0]))))

        if "extras" in child:
            kwargs["metadata"] = child["extras"]

        if "mesh" in child:
            geometries = mesh_prim[child["mesh"]]

            # if the node has a mesh associated with it
            if len(geometries) > 1:
                # append root node
                graph.append(kwargs.copy())
                # put primitives as children
                for i, geom_name in enumerate(geometries):
                    # save the name of the geometry
                    kwargs["geometry"] = geom_name
                    # no transformations
                    kwargs["matrix"] = np.eye(4)
                    kwargs["frame_from"] = names[b]
                    # if we have more than one primitive assign a new UUID
                    # frame name for the primitives after the first one
                    frame_to = "{}_{}".format(names[b], util.unique_id(length=6))
                    kwargs["frame_to"] = frame_to
                    # append the edge with the mesh frame
                    graph.append(kwargs.copy())
            elif len(geometries) == 1:
                kwargs["geometry"] = geometries[0]
                if "name" in child:
                    kwargs["frame_to"] = names[b]
                graph.append(kwargs.copy())
        else:
            # if the node doesn't have any geometry just add
            graph.append(kwargs)

    # kwargs for load_kwargs
    result = {"class": "Scene", "geometry": meshes, "graph": graph, "base_frame": base_frame}
    try:
        # load any scene extras into scene.metadata
        # use a try except to avoid nested key checks
        result["metadata"] = header["scenes"][header["scene"]]["extras"]
    except BaseException:
        pass

    return result
