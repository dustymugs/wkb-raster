import numpy as np
import os
import pickle
import unittest

import wkb_raster

class TestWKBRasterWrite(unittest.TestCase):

    def setUp(self):

        self.data_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                'data'
            )
        )

        self.source_files = [
            os.path.join(self.data_dir, f)
            for f in os.listdir(self.data_dir)
            if (
                os.path.isfile(os.path.join(self.data_dir, f)) and
                f.startswith('wkb_') and
                f.endswith('.expected')
            )
        ]

    def test_write(self):

        for source_file in self.source_files:

            expected_file = source_file.replace('.expected', '')

            with open(source_file, 'rb') as fh:

                testing = pickle.load(fh)

            with open(expected_file, 'rb') as fh:

                expected = fh.read()

            self.assertEqual(wkb_raster.write(testing), expected)
