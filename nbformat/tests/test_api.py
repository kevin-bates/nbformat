"""Test the APIs at the top-level of nbformat"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import json
import os
import pathlib
import sys
import unittest

from .base import TestsBase
from jsonschema import ValidationError

from tempfile import TemporaryDirectory
from ..reader import get_version
from ..validator import isvalid
from nbformat import read, current_nbformat, writes, write


class TestAPI(TestsBase):

    def test_read(self):
        """Can older notebooks be opened and automatically converted to the current 
        nbformat?"""

        # Open a version 2 notebook.
        with self.fopen(u'test2.ipynb', 'r') as f:
            nb = read(f, as_version=current_nbformat)

        # Check that the notebook was upgraded to the latest version automatically.
        (major, minor) = get_version(nb)
        self.assertEqual(major, current_nbformat)

    def test_write_downgrade_2(self):
        """dowgrade a v3 notebook to v2"""
        # Open a version 3 notebook.
        with self.fopen(u'test3.ipynb', 'r') as f:
            nb = read(f, as_version=3)

        jsons = writes(nb, version=2)
        nb2 = json.loads(jsons)
        (major, minor) = get_version(nb2)
        self.assertEqual(major, 2)

    def test_read_write_path(self):
        """read() and write() take filesystem paths"""
        path = os.path.join(self._get_files_path(), u'test4.ipynb')
        nb = read(path, as_version=4)

        with TemporaryDirectory() as td:
            dest = os.path.join(td, 'echidna.ipynb')
            write(nb, dest)
            assert os.path.isfile(dest)

    @unittest.skipIf(
        sys.version_info < (3, 6, 0),
        "python versions 3.5 and lower don't support opening pathlib.Path objects"
    )
    def test_read_write_pathlib_object(self):
        """read() and write() take path-like objects such as pathlib objects"""
        path = pathlib.Path(self._get_files_path()) / u'test4.ipynb'
        nb = read(path, as_version=4)

        with TemporaryDirectory() as td:
            dest = pathlib.Path(td) / 'echidna.ipynb'
            write(nb, dest)
            assert os.path.isfile(dest)

    def test_capture_validation_error(self):
        """Test that validation error can be captured on read() and write()"""
        validation_error = {}
        path = os.path.join(self._get_files_path(), u'invalid.ipynb')
        nb = read(path, as_version=4, capture_validation_error=validation_error)
        assert not isvalid(nb)
        assert 'ValidationError' in validation_error
        assert isinstance(validation_error['ValidationError'], ValidationError)

        validation_error = {}
        with TemporaryDirectory() as td:
            dest = os.path.join(td, 'invalid.ipynb')
            write(nb, dest, capture_validation_error=validation_error)
            assert os.path.isfile(dest)
            assert 'ValidationError' in validation_error
            assert isinstance(validation_error['ValidationError'], ValidationError)

        # Repeat with a valid notebook file
        validation_error = {}
        path = os.path.join(self._get_files_path(), u'test4.ipynb')
        nb = read(path, as_version=4, capture_validation_error=validation_error)
        assert isvalid(nb)
        assert 'ValidationError' not in validation_error

        validation_error = {}
        with TemporaryDirectory() as td:
            dest = os.path.join(td, 'test4.ipynb')
            write(nb, dest, capture_validation_error=validation_error)
            assert os.path.isfile(dest)
            assert 'ValidationError' not in validation_error
