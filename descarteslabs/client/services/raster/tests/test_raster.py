# Copyright 2018 Descartes Labs.
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

import io
import json
import os
import re
import sys
import tempfile
import unittest

from descarteslabs.client.addons import blosc, numpy as np, ThirdParty
from descarteslabs.client.auth import Auth
import descarteslabs.client.services.raster.raster
from descarteslabs.client.services.raster.raster import as_json_string, Raster

import responses
try:
    import mock
except ImportError:
    from unittest import mock

public_token = "header.e30.signature"
a_geometry = {
    "coordinates": ((
        (-95.66055514862535, 41.24469400862013),
        (-94.74931826062456, 41.26199387228942),
        (-94.76311013534223, 41.95357639323731),
        (-95.69397431605952, 41.93542085595837),
        (-95.66055514862535, 41.24469400862013)
    ),),
    "type": "Polygon"
}


class RasterTest(unittest.TestCase):

    def setUp(self):
        self.url = "http://example.com/raster"
        self.raster = Raster(url=self.url, auth=Auth(jwt_token=public_token, token_info_path=None))
        self.match_url = re.compile(self.url)

    def mock_response(self, method, json, status=200, **kwargs):
        responses.add(method, self.match_url, json=json, status=status, **kwargs)

    def create_blosc_response(self, metadata, array):
        array_meta = {"shape": array.shape, "dtype": array.dtype.name, "chunks": [1]}
        array_ptr = array.__array_interface__['data'][0]
        blosc_data = blosc.compress_ptr(array_ptr, array.size, array.dtype.itemsize).decode("utf-8")
        return "\n".join([json.dumps(metadata), json.dumps(array_meta), blosc_data])

    @responses.activate
    def test_dltiles_from_shape(self):
        self.mock_response(responses.POST, {
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "count": 1,
                    },
                },
                {
                    "type": "Feature",
                    "properties": {
                        "count": 2,
                    },
                },
            ]
        })
        tiles = self.raster.dltiles_from_shape(30.0, 2048, 16, a_geometry)
        self.assertEqual([1, 2], [t.properties.count for t in tiles.features])

    @responses.activate
    def test_iter_dltiles_from_shape(self):
        self.mock_response(responses.POST, {
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "count": 1,
                    },
                },
            ],
            "iterstate": {
                "start_zone": None,
                "start_ti": None,
                "start_tj": None,
            }
        })
        self.mock_response(responses.POST, {
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "count": 2,
                    },
                },
            ]
        })
        tiles = self.raster.dltiles_from_shape(30.0, 2048, 16, a_geometry)
        self.assertEqual([1, 2], [t.properties.count for t in tiles.features])

    def test_dltile_invalid(self):
        with self.assertRaises(ValueError):
            self.raster.dltile(None)
        with self.assertRaises(ValueError):
            self.raster.dltile('')

    @responses.activate
    def test_raster(self):
        raster_meta = {"files": 1, "metadata": {"foo": "bar"}}
        file_meta = {"name": "mosaic.tiff", "length": 42}
        file_data = "o" * 42
        response = "\n".join([json.dumps(raster_meta), json.dumps(file_meta), file_data])
        self.mock_response(responses.POST, json=None, body=response)
        raster = self.raster.raster(["fakeid"])
        self.assertEqual(file_data.encode("utf-8"), raster["files"]["mosaic.tiff"])
        self.assertEqual(raster_meta["metadata"], raster["metadata"])

    @responses.activate
    def test_raster_save(self):
        raster_meta = {"files": 1, "metadata": {}}
        file_meta = {"name": "mosaic.tiff", "length": 42}
        file_data = "o" * 42
        response = "\n".join([json.dumps(raster_meta), json.dumps(file_meta), file_data])
        self.mock_response(responses.POST, json=None, body=response)

        with tempfile.NamedTemporaryFile(suffix=".tiff") as temp:
            temp.close()  # For Windows compatibility
            raster = self.raster.raster(["fakeid"], outfile_basename=os.path.splitext(temp.name)[0], save=True)
            self.assertEqual(file_data.encode("utf-8"), raster["files"][temp.name])
            with open(temp.name) as data:
                self.assertEqual(file_data, data.read())

    @responses.activate
    @mock.patch.object(descarteslabs.client.services.raster.raster, "blosc", ThirdParty("blosc"))
    def test_ndarray_no_blosc(self):
        expected_array = np.zeros((2, 2))
        expected_metadata = {"foo": "bar"}
        content = io.BytesIO()
        np.savez(content, data=expected_array, metadata=json.dumps(expected_metadata).encode("utf-8"))
        self.mock_response(responses.POST, json=None, body=content.getvalue())
        array, meta = self.raster.ndarray(["fakeid"])
        self.assertEqual(expected_metadata, meta)
        np.testing.assert_array_equal(expected_array, array)

    @unittest.skipIf(sys.platform.startswith("win"), "no blosc on Windows")
    @responses.activate
    def test_ndarray_blosc(self):
        expected_metadata = {"foo": "bar"}
        expected_array = np.zeros((2, 2))
        content = self.create_blosc_response(expected_metadata, expected_array)
        self.mock_response(responses.POST, json=None, body=content, stream=True)
        array, meta = self.raster.ndarray(["fakeid"])
        self.assertEqual(expected_metadata, meta)
        np.testing.assert_array_equal(expected_array, array)

    @responses.activate
    def do_stack(self, **stack_args):
        expected_metadata = {"foo": "bar"}
        expected_array = np.zeros((2, 2, 1))
        content = self.create_blosc_response(expected_metadata, expected_array)
        self.mock_response(responses.POST, json=None, body=content, stream=True)
        stack, meta = self.raster.stack(
            [["fakeid"], ["fakeid2"]],
            order="gdal",
            **stack_args
        )
        np.testing.assert_array_equal(expected_array, stack[0, :])
        np.testing.assert_array_equal(expected_array, stack[1, :])
        self.assertEqual([expected_metadata] * 2, meta)

    @unittest.skipIf(sys.platform.startswith("win"), "no blosc on Windows")
    @mock.patch.object(descarteslabs.client.services.raster.raster, "concurrent", ThirdParty("concurrent"))
    def test_stack_serial_blosc(self):
        self.do_stack(
            resolution=60,
            srs="EPSG:32615",
            bounds=(277280.0, 4569600.0, 354080.0, 4646400.0),
            bands=["red"],
        )

    @unittest.skipIf(sys.platform.startswith("win"), "no blosc on Windows")
    def test_stack_threaded_blosc(self):
        self.do_stack(
            resolution=60,
            srs="EPSG:32615",
            bounds=(277280.0, 4569600.0, 354080.0, 4646400.0),
            bands=["red"],
        )

    @unittest.skipIf(sys.platform.startswith("win"), "no blosc on Windows")
    def test_stack_dltile_blosc(self):
        self.do_stack(
            dltile="128:16:960.0:15:-2:37",
            bands=["red"],
        )

    def test_stack_underspecified(self):
        keys = ["landsat:LC08:PRE:TOAR:meta_LC80270312016188_v1"]
        place = "north-america_united-states_iowa"
        bounds = (-95.69397431605952, 41.24469400862013, -94.74931826062456, 41.95357639323731)
        resolution = 960
        dimensions = (128, 128)
        srs = "EPSG:32615"

        with self.assertRaises(ValueError):
            self.raster.stack(keys)
        with self.assertRaises(ValueError):
            self.raster.stack(keys, resolution=resolution)
        with self.assertRaises(ValueError):
            self.raster.stack(keys, dimensions=dimensions)
        with self.assertRaises(ValueError):
            self.raster.stack(keys, bounds=bounds)
        with self.assertRaises(ValueError):
            self.raster.stack(keys, resolution=resolution, cutline=a_geometry)
        with self.assertRaises(ValueError):
            self.raster.stack(keys, resolution=resolution, cutline=a_geometry, bounds=bounds)
        with self.assertRaises(ValueError):
            self.raster.stack(keys, resolution=resolution, cutline=a_geometry, srs=srs)
        with self.assertRaises(ValueError):
            self.raster.stack(keys, resolution=resolution, place=place)


class UtilitiesTest(unittest.TestCase):

    def test_as_json_string(self):
        d = {'a': 'b'}
        truth = json.dumps(d)

        self.assertEqual(as_json_string(d), truth)
        s = '{"a": "b"}'
        self.assertEqual(as_json_string(s), truth)
        self.assertEqual(as_json_string(None), None)


if __name__ == "__main__":
    unittest.main()
