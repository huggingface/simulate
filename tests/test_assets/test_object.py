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
import logging

# Lint as: python3
# flake8: noqa
import unittest

import numpy as np
import pyvista as pv

import simulate as sm


logger = logging.getLogger(__name__)


# Create simple versions from all objects
ALL_OBJECTS = [
    (sm.Object3D, {}),
    (sm.Plane, {}),
    (sm.Sphere, {"theta_resolution": 5, "phi_resolution": 5}),
    (sm.Capsule, {"theta_resolution": 5, "phi_resolution": 5}),
    (sm.Cylinder, {"resolution": 5}),
    (sm.Box, {}),
    (sm.Cone, {}),
    (sm.Line, {}),
    (sm.MultipleLines, {}),
    (sm.Tube, {}),
    (sm.Polygon, {"points": [[-1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 0.0, -1.0]]}),
    (sm.RegularPolygon, {}),
    (sm.Ring, {}),
    (sm.Text3D, {}),
    (sm.Triangle, {}),
    (sm.Rectangle, {}),
    (sm.Circle, {"resolution": 10}),
    (
        sm.StructuredGrid,
        {
            "x": [[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]],
            "y": [
                [0.69006556, 0.9534626, 0.69006556],
                [0.9534626, 3.1622777, 0.9534626],
                [0.69006556, 0.9534626, 0.69006556],
            ],
            "z": [[-1.0, -1.0, -1.0], [0.0, 0.0, 0.0], [1.0, 1.0, 1.0]],
        },
    ),
]


# fmt: off
class ObjectsTest(unittest.TestCase):
    def test_create_asset(self):
        asset = sm.Object3D(name="object")

        self.assertEqual(len(asset.mesh.points), 0)
        self.assertTupleEqual(asset.mesh.points.shape, (0, 3))

        self.assertListEqual(asset.material.base_color, [1.0, 1.0, 1.0, 1.0])

        with self.assertRaises(ValueError):
            asset.plot()  # Cannot plot empty meshes

    def test_extra_assets_parameters(self):
        for cls, kwargs in ALL_OBJECTS:
            print(cls, kwargs)
            # position
            position=[3, 3, 3]
            asset = cls(position=position, **kwargs)
            self.assertIsInstance(asset, cls)
            self.assertAlmostEqual(sum(asset.position), sum(position))

            # rotation
            rotation=[0, 1, 0, 0]
            asset = cls(rotation=rotation, **kwargs)
            self.assertIsInstance(asset, cls)
            self.assertAlmostEqual(sum(asset.rotation), sum(rotation))

            # scaling
            scaling=[3, 3, 3]
            asset = cls(scaling=scaling, **kwargs)
            self.assertIsInstance(asset, cls)
            self.assertAlmostEqual(sum(asset.scaling), sum(scaling))

            # parent
            parent = sm.Asset(name="mummy")
            asset = cls(parent=parent, **kwargs)
            self.assertIsInstance(asset, cls)
            self.assertEqual(asset.tree_parent.name, "mummy")

            # children
            child = sm.Asset(name="babby")
            asset = cls(children=child, **kwargs)
            self.assertIsInstance(asset, cls)
            self.assertEqual(asset.tree_children[0].name, "babby")

            asset = cls(children=[child], **kwargs)
            self.assertIsInstance(asset, cls)
            self.assertEqual(asset.tree_children[0].name, "babby")

    def test_plane(self):
        asset = sm.Plane()
        default_mesh = np.array([[ 5.000000e+00,  0, -5.000000e+00],
                 [-5.000000e+00, -0, -5.000000e+00],
                 [ 5.000000e+00,  0,  5.000000e+00],
                 [-5.000000e+00, -0,  5.000000e+00]])
        np.testing.assert_allclose(asset.mesh.points, default_mesh, atol=1e-5)

    def test_sphere(self):
        asset = sm.Sphere(theta_resolution=5, phi_resolution=5, with_collider=True)
        default_faces = np.array(
            [ 
               3,  2,  5,  0,  3,  5,  8,  0,  3,  8, 11,  0,  3, 11, 14,  0,  3,
               14,  2,  0,  3,  4,  1,  7,  3,  7,  1, 10,  3, 10,  1, 13,  3, 13,
               1, 16,  3, 16,  1,  4,  4,  2,  3,  6,  5,  4,  3,  4,  7,  6,  4,
               5,  6,  9,  8,  4,  6,  7, 10,  9,  4,  8,  9, 12, 11,  4,  9, 10,
               13, 12,  4, 11, 12, 15, 14,  4, 12, 13, 16, 15,  4, 14, 15,  3,  2,
               4, 15, 16,  4,  3
            ]
        )
        np.testing.assert_allclose(asset.mesh.faces, default_faces, atol=1e-5)

        default_mesh = np.array([[-1.0000000e+00,  0.0000000e+00,  1.1102230e-16],
                 [ 1.0000000e+00,  0.0000000e+00, -1.1102230e-16],
                 [-7.0710677e-01,  0.0000000e+00,  7.0710677e-01],
                 [ 4.9789960e-17,  0.0000000e+00,  1.0000000e+00],
                 [ 7.0710677e-01,  0.0000000e+00,  7.0710677e-01],
                 [-7.0710677e-01,  6.7249852e-01,  2.1850801e-01],
                 [-2.6924564e-17,  9.5105654e-01,  3.0901700e-01],
                 [ 7.0710677e-01,  6.7249852e-01,  2.1850801e-01],
                 [-7.0710677e-01,  4.1562694e-01, -5.7206142e-01],
                 [-1.5105128e-16,  5.8778524e-01, -8.0901700e-01],
                 [ 7.0710677e-01,  4.1562694e-01, -5.7206142e-01],
                 [-7.0710677e-01, -4.1562694e-01, -5.7206142e-01],
                 [-1.5105128e-16, -5.8778524e-01, -8.0901700e-01],
                 [ 7.0710677e-01, -4.1562694e-01, -5.7206142e-01],
                 [-7.0710677e-01, -6.7249852e-01,  2.1850801e-01],
                 [-2.6924564e-17, -9.5105654e-01,  3.0901700e-01],
                 [ 7.0710677e-01, -6.7249852e-01,  2.1850801e-01]])
        np.testing.assert_allclose(asset.mesh.points, default_mesh, atol=1e-5)

        self.assertTrue(any(isinstance(node, sm.Collider) for node in asset.tree_children))
        self.assertTrue(any(bool(isinstance(node, sm.Collider) and node.type == "sphere") for node in asset.tree_children))
        self.assertTrue(any(bool(isinstance(node, sm.Collider) and node.bounding_box == [1.0, 1.0, 1.0]) for node in asset.tree_children))
    

    def test_capsule(self):
        asset = sm.Capsule(theta_resolution=5, phi_resolution=5, with_collider=True)
        default_faces = np.array([ 3,  0,  1,  7,  3,  0,  7, 13,  3,  0, 13, 19,  3,  0, 19, 25,  3,
        0, 25, 31,  3,  0, 31, 37,  3,  0, 37, 43,  3,  6, 49, 12,  3, 12,
       49, 18,  3, 18, 49, 24,  3, 24, 49, 30,  3, 30, 49, 36,  3, 36, 49,
       42,  3, 42, 49, 48,  3, 57, 51, 50,  3, 63, 57, 50,  3, 69, 63, 50,
        3, 75, 69, 50,  3, 81, 75, 50,  3, 87, 81, 50,  3, 93, 87, 50,  3,
       56, 62, 99,  3, 62, 68, 99,  3, 68, 74, 99,  3, 74, 80, 99,  3, 80,
       86, 99,  3, 86, 92, 99,  3, 92, 98, 99,  4,  1,  2,  8,  7,  4, 51,
       57, 58, 52,  4,  2,  3,  9,  8,  4, 52, 58, 59, 53,  4,  3,  4, 10,
        9,  4, 53, 59, 60, 54,  4,  4,  5, 11, 10,  4, 54, 60, 61, 55,  4,
        5,  6, 12, 11,  4, 55, 61, 62, 56,  4,  7,  8, 14, 13,  4, 57, 63,
       64, 58,  4,  8,  9, 15, 14,  4, 58, 64, 65, 59,  4,  9, 10, 16, 15,
        4, 59, 65, 66, 60,  4, 10, 11, 17, 16,  4, 60, 66, 67, 61,  4, 11,
       12, 18, 17,  4, 61, 67, 68, 62,  4, 13, 14, 20, 19,  4, 63, 69, 70,
       64,  4, 14, 15, 21, 20,  4, 64, 70, 71, 65,  4, 15, 16, 22, 21,  4,
       65, 71, 72, 66,  4, 16, 17, 23, 22,  4, 66, 72, 73, 67,  4, 17, 18,
       24, 23,  4, 67, 73, 74, 68,  4, 19, 20, 26, 25,  4, 69, 75, 76, 70,
        4, 20, 21, 27, 26,  4, 70, 76, 77, 71,  4, 21, 22, 28, 27,  4, 71,
       77, 78, 72,  4, 22, 23, 29, 28,  4, 72, 78, 79, 73,  4, 23, 24, 30,
       29,  4, 73, 79, 80, 74,  4, 25, 26, 32, 31,  4, 75, 81, 82, 76,  4,
       26, 27, 33, 32,  4, 76, 82, 83, 77,  4, 27, 28, 34, 33,  4, 77, 83,
       84, 78,  4, 28, 29, 35, 34,  4, 78, 84, 85, 79,  4, 29, 30, 36, 35,
        4, 79, 85, 86, 80,  4, 31, 32, 38, 37,  4, 81, 87, 88, 82,  4, 32,
       33, 39, 38,  4, 82, 88, 89, 83,  4, 33, 34, 40, 39,  4, 83, 89, 90,
       84,  4, 34, 35, 41, 40,  4, 84, 90, 91, 85,  4, 35, 36, 42, 41,  4,
       85, 91, 92, 86,  4, 37, 38, 44, 43,  4, 87, 93, 94, 88,  4, 38, 39,
       45, 44,  4, 88, 94, 95, 89,  4, 39, 40, 46, 45,  4, 89, 95, 96, 90,
        4, 40, 41, 47, 46,  4, 90, 96, 97, 91,  4, 41, 42, 48, 47,  4, 91,
       97, 98, 92,  3,  0, 50,  1,  3,  1, 50, 51,  3,  1, 51,  2,  3,  2,
       51, 52,  3,  2, 52,  3,  3,  3, 52, 53,  3,  3, 53,  4,  3,  4, 53,
       54,  3,  4, 54,  5,  3,  5, 54, 55,  3,  5, 55,  6,  3,  6, 55, 56,
        3, 49, 99, 48,  3, 48, 99, 98,  3, 48, 98, 47,  3, 47, 98, 97,  3,
       47, 97, 46,  3, 46, 97, 96,  3, 46, 96, 45,  3, 45, 96, 95,  3, 45,
       95, 44,  3, 44, 95, 94,  3, 44, 94, 43,  3, 43, 94, 93,  4,  6, 56,
       99, 49,  4, 43, 93, 50,  0])
        np.testing.assert_allclose(asset.mesh.faces, default_faces, atol=1e-5)

        dafault_mesh = np.array([[ 0.        ,  0.3       ,  0.2       ],
                 [ 0.08677675,  0.3       ,  0.18019377],
                 [ 0.1563663 ,  0.3       ,  0.12469796],
                 [ 0.19498558,  0.3       ,  0.04450419],
                 [ 0.19498558,  0.3       , -0.04450419],
                 [ 0.1563663 ,  0.3       , -0.12469796],
                 [ 0.08677675,  0.3       , -0.18019377],
                 [ 0.07818315,  0.337651  ,  0.18019377],
                 [ 0.14088117,  0.3678448 ,  0.12469796],
                 [ 0.17567594,  0.3846011 ,  0.04450419],
                 [ 0.17567594,  0.3846011 , -0.04450419],
                 [ 0.14088117,  0.3678448 , -0.12469796],
                 [ 0.07818315,  0.337651  , -0.18019377],
                 [ 0.05410442,  0.3678448 ,  0.18019377],
                 [ 0.09749279,  0.4222521 ,  0.12469796],
                 [ 0.12157152,  0.45244586,  0.04450419],
                 [ 0.12157152,  0.45244586, -0.04450419],
                 [ 0.09749279,  0.4222521 , -0.12469796],
                 [ 0.05410442,  0.3678448 , -0.18019377],
                 [ 0.01930964,  0.3846011 ,  0.18019377]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

        self.assertTrue(any(isinstance(node, sm.Collider) for node in asset.tree_children))
        self.assertTrue(any(bool(isinstance(node, sm.Collider) and node.type == "capsule") for node in asset.tree_children))
        self.assertTrue(any(bool(isinstance(node, sm.Collider) and node.bounding_box == [0.2, 1.0, 0.2]) for node in asset.tree_children))

    def test_cylinder(self):
        asset = sm.Cylinder(resolution=5)
        default_faces = np.array([ 4,  0,  1,  3,  2,  4, 22, 23,  5,  4,  4, 24, 25,  7,  6,  4, 26,
            27,  9,  8,  4, 28, 29, 21, 20,  5, 10, 11, 12, 13, 14,  5, 15, 16,
            17, 18, 19])
        np.testing.assert_allclose(asset.mesh.faces, default_faces, atol=1e-5)

        dafault_mesh = np.array([[ 0.        ,  0.5       , -1.        ],
                 [ 0.        , -0.5       , -1.        ],
                 [-0.95105654,  0.5       , -0.309017  ],
                 [-0.95105654, -0.5       , -0.309017  ],
                 [-0.58778524,  0.5       ,  0.809017  ],
                 [-0.58778524, -0.5       ,  0.809017  ],
                 [ 0.58778524,  0.5       ,  0.809017  ],
                 [ 0.58778524, -0.5       ,  0.809017  ],
                 [ 0.95105654,  0.5       , -0.309017  ],
                 [ 0.95105654, -0.5       , -0.309017  ],
                 [ 0.        ,  0.5       , -1.        ],
                 [-0.95105654,  0.5       , -0.309017  ],
                 [-0.58778524,  0.5       ,  0.809017  ],
                 [ 0.58778524,  0.5       ,  0.809017  ],
                 [ 0.95105654,  0.5       , -0.309017  ],
                 [ 0.95105654, -0.5       , -0.309017  ],
                 [ 0.58778524, -0.5       ,  0.809017  ],
                 [-0.58778524, -0.5       ,  0.809017  ],
                 [-0.95105654, -0.5       , -0.309017  ],
                 [ 0.        , -0.5       , -1.        ]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

    def test_box(self):
        asset = sm.Box(with_collider=True)
        default_faces = np.array([ 4,  0,  4,  6,  2,  4,  5,  1,  3,  7,  4,  8, 10, 18, 16,  4, 20,
       22, 14, 12,  4, 11,  9, 13, 15,  4, 17, 19, 23, 21])
        np.testing.assert_allclose(asset.mesh.faces, default_faces, atol=1e-5)

        dafault_mesh = np.array([[-0.5, -0.5, -0.5],
                 [ 0.5, -0.5, -0.5],
                 [-0.5,  0.5, -0.5],
                 [ 0.5,  0.5, -0.5],
                 [-0.5, -0.5,  0.5],
                 [ 0.5, -0.5,  0.5],
                 [-0.5,  0.5,  0.5],
                 [ 0.5,  0.5,  0.5],
                 [-0.5, -0.5, -0.5],
                 [-0.5, -0.5, -0.5],
                 [ 0.5, -0.5, -0.5],
                 [ 0.5, -0.5, -0.5],
                 [-0.5,  0.5, -0.5],
                 [-0.5,  0.5, -0.5],
                 [ 0.5,  0.5, -0.5],
                 [ 0.5,  0.5, -0.5],
                 [-0.5, -0.5,  0.5],
                 [-0.5, -0.5,  0.5],
                 [ 0.5, -0.5,  0.5],
                 [ 0.5, -0.5,  0.5]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

        self.assertTrue(any(isinstance(node, sm.Collider) for node in asset.tree_children))
        self.assertTrue(any(bool(isinstance(node, sm.Collider) and node.type == "box") for node in asset.tree_children))
        self.assertTrue(any(bool(isinstance(node, sm.Collider) and node.bounding_box == [1.0, 1.0, 1.0]) for node in asset.tree_children))

    def test_cone(self):
        asset = sm.Cone()
        default_faces = np.array([ 6,  6,  5,  4,  3,  2,  1,  3,  0, 12, 14,  3,  7, 15, 16,  3,  8,
       17, 18,  3,  9, 19, 20,  3, 10, 21, 22,  3, 11, 23, 13])
        np.testing.assert_allclose(asset.mesh.faces, default_faces, atol=1e-5)

        dafault_mesh = np.array([[ 0.0000000e+00,  5.0000000e-01, -4.3297803e-17],
                 [ 1.0000000e+00, -5.0000000e-01,  1.2989340e-16],
                 [ 5.0000000e-01, -5.0000000e-01, -8.6602539e-01],
                 [-5.0000000e-01, -5.0000000e-01, -8.6602539e-01],
                 [-1.0000000e+00, -5.0000000e-01, -1.6576248e-16],
                 [-5.0000000e-01, -5.0000000e-01,  8.6602539e-01],
                 [ 5.0000000e-01, -5.0000000e-01,  8.6602539e-01],
                 [ 0.0000000e+00,  5.0000000e-01, -4.3297803e-17],
                 [ 0.0000000e+00,  5.0000000e-01, -4.3297803e-17],
                 [ 0.0000000e+00,  5.0000000e-01, -4.3297803e-17],
                 [ 0.0000000e+00,  5.0000000e-01, -4.3297803e-17],
                 [ 0.0000000e+00,  5.0000000e-01, -4.3297803e-17],
                 [ 1.0000000e+00, -5.0000000e-01,  1.2989340e-16],
                 [ 1.0000000e+00, -5.0000000e-01,  1.2989340e-16],
                 [ 5.0000000e-01, -5.0000000e-01, -8.6602539e-01],
                 [ 5.0000000e-01, -5.0000000e-01, -8.6602539e-01],
                 [-5.0000000e-01, -5.0000000e-01, -8.6602539e-01],
                 [-5.0000000e-01, -5.0000000e-01, -8.6602539e-01],
                 [-1.0000000e+00, -5.0000000e-01, -1.6576248e-16],
                 [-1.0000000e+00, -5.0000000e-01, -1.6576248e-16]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

    def test_line(self):
        asset = sm.Line()
        default_faces = np.array([])
        np.testing.assert_allclose(asset.mesh.faces, default_faces, atol=1e-5)

        dafault_mesh = np.array([[-1.,  0.,  0.],
                 [ 1.,  0.,  0.]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

    def test_multiplelines(self):
        asset = sm.MultipleLines()
        default_faces = np.array([])
        np.testing.assert_allclose(asset.mesh.faces, default_faces, atol=1e-5)

        dafault_mesh = np.array([[-1.,  0.,  0.],
                 [ 1.,  0.,  0.]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

    def test_tube(self):
        asset = sm.Tube()
        default_faces = np.array([ 3,  1,  0, 17,  3, 17,  0, 16,  3,  2,  1, 18,  3, 18,  1, 17,  3,
        3,  2, 19,  3, 19,  2, 18,  3,  4,  3, 20,  3, 20,  3, 19,  3,  5,
        4, 21,  3, 21,  4, 20,  3,  6,  5, 22,  3, 22,  5, 21,  3,  7,  6,
       23,  3, 23,  6, 22,  3,  8,  7, 24,  3, 24,  7, 23,  3,  9,  8, 25,
        3, 25,  8, 24,  3, 10,  9, 26,  3, 26,  9, 25,  3, 11, 10, 27,  3,
       27, 10, 26,  3, 12, 11, 28,  3, 28, 11, 27,  3, 13, 12, 29,  3, 29,
       12, 28,  3, 14, 13, 30,  3, 30, 13, 29,  3, 15, 14, 31,  3, 31, 14,
       30,  3,  0, 15, 16,  3, 16, 15, 31])
        np.testing.assert_allclose(asset.mesh.faces, default_faces, atol=1e-5)

        dafault_mesh = np.array([[-1.0000000e+00,  0.0000000e+00,  1.0000000e+00],
                 [-1.0000000e+00,  3.8268343e-01,  9.2387950e-01],
                 [-1.0000000e+00,  7.0710677e-01,  7.0710677e-01],
                 [-1.0000000e+00,  9.2387950e-01,  3.8268343e-01],
                 [-1.0000000e+00,  1.0000000e+00,  6.1232343e-17],
                 [-1.0000000e+00,  9.2387950e-01, -3.8268343e-01],
                 [-1.0000000e+00,  7.0710677e-01, -7.0710677e-01],
                 [-1.0000000e+00,  3.8268343e-01, -9.2387950e-01],
                 [-1.0000000e+00,  1.2246469e-16, -1.0000000e+00],
                 [-1.0000000e+00, -3.8268343e-01, -9.2387950e-01],
                 [-1.0000000e+00, -7.0710677e-01, -7.0710677e-01],
                 [-1.0000000e+00, -9.2387950e-01, -3.8268343e-01],
                 [-1.0000000e+00, -1.0000000e+00, -1.8369701e-16],
                 [-1.0000000e+00, -9.2387950e-01,  3.8268343e-01],
                 [-1.0000000e+00, -7.0710677e-01,  7.0710677e-01],
                 [-1.0000000e+00, -3.8268343e-01,  9.2387950e-01],
                 [ 1.0000000e+00,  0.0000000e+00,  1.0000000e+00],
                 [ 1.0000000e+00,  3.8268343e-01,  9.2387950e-01],
                 [ 1.0000000e+00,  7.0710677e-01,  7.0710677e-01],
                 [ 1.0000000e+00,  9.2387950e-01,  3.8268343e-01]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

    def test_polygon(self):
        asset = sm.Polygon(points=[[-1.,  0.,  0.], [0.,  0.,  1.],
                 [ 1.,  0.,  0.],
                 [ 0.,  0.,  -1.]])
        default_faces = np.array([4, 0, 1, 2, 3])
        np.testing.assert_allclose(asset.mesh.faces, default_faces, atol=1e-5)

        dafault_mesh = np.array([[-1.,  0.,  0.],
                 [ 0.,  0.,  1.],
                 [ 1.,  0.,  0.],
                 [ 0.,  0., -1.]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

    def test_regular_polygon(self):
        asset = sm.RegularPolygon()
        default_faces = np.array([6, 0, 1, 2, 3, 4, 5])
        np.testing.assert_allclose(asset.mesh.faces, default_faces, atol=1e-5)

        dafault_mesh = np.array([[ 0.0000000e+00,  0.0000000e+00, -1.0000000e+00],
                 [ 8.6602539e-01,  0.0000000e+00, -5.0000000e-01],
                 [ 8.6602539e-01,  0.0000000e+00,  5.0000000e-01],
                 [ 1.2246469e-16,  0.0000000e+00,  1.0000000e+00],
                 [-8.6602539e-01,  0.0000000e+00,  5.0000000e-01],
                 [-8.6602539e-01,  0.0000000e+00, -5.0000000e-01]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

    def test_ring(self):
        asset = sm.Ring()
        default_faces = np.array([ 4,  0,  1,  3,  2,  4,  2,  3,  5,  4,  4,  4,  5,  7,  6,  4,  6,
        7,  9,  8,  4,  8,  9, 11, 10,  4, 10, 11,  1,  0])
        np.testing.assert_allclose(asset.mesh.faces, default_faces, atol=1e-5)

        dafault_mesh = np.array([[-2.5000000e-01,  2.7755576e-17,  0.0000000e+00],
                 [-5.0000000e-01,  5.5511151e-17,  0.0000000e+00],
                 [-1.2500000e-01,  1.3877788e-17,  2.1650635e-01],
                 [-2.5000000e-01,  2.7755576e-17,  4.3301269e-01],
                 [ 1.2500000e-01, -1.3877788e-17,  2.1650635e-01],
                 [ 2.5000000e-01, -2.7755576e-17,  4.3301269e-01],
                 [ 2.5000000e-01, -2.7755576e-17,  3.0616171e-17],
                 [ 5.0000000e-01, -5.5511151e-17,  6.1232343e-17],
                 [ 1.2500000e-01, -1.3877788e-17, -2.1650635e-01],
                 [ 2.5000000e-01, -2.7755576e-17, -4.3301269e-01],
                 [-1.2500000e-01,  1.3877788e-17, -2.1650635e-01],
                 [-2.5000000e-01,  2.7755576e-17, -4.3301269e-01]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

    def test_text3d(self):
        asset = sm.Text3D()
        default_faces = np.array([  3,   4,   9,   7,   3, 161, 163, 158,   3,   0,   5,  13,   3,
       167, 159, 154,   3,   5,  10,  13])
        np.testing.assert_allclose(asset.mesh.faces[:20], default_faces, atol=1e-5)

        dafault_mesh = np.array([[ 2.68570006e-01, -7.18600005e-02, -2.98172604e-17],
                 [ 4.05710012e-01, -7.18600005e-02, -4.50428596e-17],
                 [ 9.88569975e-01, -7.29499981e-02, -1.09753315e-16],
                 [ 9.82860029e-01, -6.87799975e-02, -1.09119383e-16],
                 [ 1.12571001e+00, -6.87799975e-02, -1.24978917e-16],
                 [ 4.09909993e-01,  4.37139988e-01, -4.55091513e-17],
                 [ 4.17140007e-01,  4.44370002e-01, -4.63118440e-17],
                 [ 9.77140009e-01,  4.43289995e-01, -1.08484334e-16],
                 [ 4.17140007e-01,  5.72770000e-01, -4.63118440e-17],
                 [ 9.77140009e-01,  5.73849976e-01, -1.08484334e-16],
                 [ 4.09909993e-01,  5.79999983e-01, -4.55091513e-17],
                 [ 9.85499978e-01,  1.02570999e+00, -1.09412477e-16],
                 [ 1.12571001e+00,  1.02306998e+00, -1.24978917e-16],
                 [ 2.68570006e-01,  1.02614999e+00, -2.98172604e-17],
                 [ 4.05710012e-01,  1.02614999e+00, -4.50428596e-17],
                 [ 1.12000000e+00,  1.02723002e+00, -1.24344979e-16],
                 [ 1.67428398e+00, -9.00899991e-02, -1.85882863e-16],
                 [ 1.73714399e+00, -9.00899991e-02, -1.92861726e-16],
                 [ 1.58285391e+00, -7.46200010e-02, -1.75732086e-16],
                 [ 1.84000397e+00, -7.10100010e-02, -2.04281477e-16]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

    def test_triangle(self):
        asset = sm.Triangle()
        default_faces = np.array([3, 0, 1, 2])
        np.testing.assert_allclose(asset.mesh.faces[:20], default_faces, atol=1e-5)

        dafault_mesh = np.array([[0.        , 0.        , 0.        ],
                 [1.        , 0.        , 0.        ],
                 [0.5       , 0.70710678, 0.        ]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

    def test_rectangle(self):
        asset = sm.Rectangle()
        default_faces = np.array([4, 0, 1, 2, 3])
        np.testing.assert_allclose(asset.mesh.faces[:20], default_faces, atol=1e-5)

        dafault_mesh = np.array([[1., 0., 0.],
                 [1., 1., 0.],
                 [0., 1., 0.],
                 [0., 0., 0.]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

    def test_circle(self):
        asset = sm.Circle(resolution=10)
        default_faces = np.array([10,  0,  1,  2,  3,  4,  5,  6,  7,  8,  9])
        np.testing.assert_allclose(asset.mesh.faces[:20], default_faces, atol=1e-5)

        dafault_mesh = np.array([[ 0.00000000e+00,  5.55111512e-17,  5.00000000e-01],
                 [-3.21393805e-01,  4.25240089e-17,  3.83022222e-01],
                 [-4.92403877e-01,  9.63941025e-18,  8.68240888e-02],
                 [-4.33012702e-01, -2.77555756e-17, -2.50000000e-01],
                 [-1.71010072e-01, -5.21634192e-17, -4.69846310e-01],
                 [ 1.71010072e-01, -5.21634192e-17, -4.69846310e-01],
                 [ 4.33012702e-01, -2.77555756e-17, -2.50000000e-01],
                 [ 4.92403877e-01,  9.63941025e-18,  8.68240888e-02],
                 [ 3.21393805e-01,  4.25240089e-17,  3.83022222e-01],
                 [ 1.22464680e-16,  5.55111512e-17,  5.00000000e-01]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

    def test_structured_grid(self):
        # let's make a sort of cone
        xrng = np.arange(-2, 3, dtype=np.float32)
        zrng = np.arange(-2, 3, dtype=np.float32)
        x, z = np.meshgrid(xrng, zrng)  # A 5X5 meshgrid
        y = 1. / np.sqrt(x*x + z*z + 0.1)

        asset = sm.StructuredGrid(x, y, z)
        default_faces = np.array([4, 0, 5, 6, 1, 4, 1, 6, 7, 2, 4, 2, 7, 8, 3, 4, 3, 8, 9, 4])
        np.testing.assert_allclose(asset.mesh.faces[:20], default_faces, atol=1e-5)

        dafault_mesh = np.array([[-2.        ,  0.35136417, -2.        ],
                 [-1.        ,  0.44280744, -2.        ],
                 [ 0.        ,  0.4938648 , -2.        ],
                 [ 1.        ,  0.44280744, -2.        ],
                 [ 2.        ,  0.35136417, -2.        ],
                 [-2.        ,  0.44280744, -1.        ],
                 [-1.        ,  0.69006556, -1.        ],
                 [ 0.        ,  0.9534626 , -1.        ],
                 [ 1.        ,  0.69006556, -1.        ],
                 [ 2.        ,  0.44280744, -1.        ],
                 [-2.        ,  0.4938648 ,  0.        ],
                 [-1.        ,  0.9534626 ,  0.        ],
                 [ 0.        ,  3.1622777 ,  0.        ],
                 [ 1.        ,  0.9534626 ,  0.        ],
                 [ 2.        ,  0.4938648 ,  0.        ],
                 [-2.        ,  0.44280744,  1.        ],
                 [-1.        ,  0.69006556,  1.        ],
                 [ 0.        ,  0.9534626 ,  1.        ],
                 [ 1.        ,  0.69006556,  1.        ],
                 [ 2.        ,  0.44280744,  1.        ]])
        np.testing.assert_allclose(asset.mesh.points[:20], dafault_mesh, atol=1e-5)

    # def test_procgen_grid(self):
    #     # TODO (Alicia): add a test for procgen grid
    #     pass

    def test_procgen_prims(self):
        # TODO (Ed): add a test for procgen prims
        pass

# fmt: on


if __name__ == "__main__":
    t = ObjectsTest()
    t.test_sphere()
