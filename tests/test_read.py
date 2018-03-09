import numpy as np
import os
import pickle
import unittest

import wkb_raster

class TestWKBRasterRead(unittest.TestCase):

    def setUp(self):

        self.data_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                'data'
            )
        )

        self.wkb_files = [
            os.path.join(self.data_dir, f)
            for f in os.listdir(self.data_dir)
            if (
                os.path.isfile(os.path.join(self.data_dir, f)) and
                f.startswith('wkb_') and
                not f.endswith('.expected')
            )
        ]

    def test_read(self):

        for wkb_file in self.wkb_files:

            expected_file = '{}.expected'.format(wkb_file)

            #if not os.path.exists(expected_file):
            #    with open(wkb_file, 'rb') as fh:
            #        with open(expected_file, 'wb') as out:
            #            pickle.dump(
            #                wkb_raster.read(fh),
            #                out,
            #                protocol=2
            #            )
            #    continue

            with open(expected_file, 'rb') as fh:

                expected = pickle.load(fh)

            with open(wkb_file, 'rb') as fh:

                testing = wkb_raster.read(fh)

            for k, v in expected.items():

                self.assertIn(k, testing)

                if k != 'bands':
                    self.assertEqual(testing[k], v)
                    continue

                test_bands = testing['bands']
                self.assertEqual(
                    len(test_bands),
                    len(v)
                )

                for idx, band in enumerate(v):

                    test_band = test_bands[idx]

                    for a, b in band.items():

                        self.assertIn(a, test_band)

                        if not isinstance(b, np.ndarray):
                            self.assertEqual(test_band[a], b)
                            continue

                        self.assertTrue(np.array_equal(test_band[a], b))