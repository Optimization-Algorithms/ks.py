#! /usr/bin/python

import unittest

from ks_engine.config_loader import check_config, DEFAULT_CONF


class TestConfigLoader(unittest.TestCase):
    def test_default_config(self):
        try:
            check_config(DEFAULT_CONF)
        except ValueError as err:
            self.assertTrue(False, err.args)

    def test_correct_config(self):
        corr_conf = {
            "TIME_LIMIT": 1245,
            "NUM_THREAD": 4,
            "MIN_GAP": 1e-10,
            "BUCKET_SIZE": 45,
        }
        try:
            check_config(DEFAULT_CONF)
        except ValueError as err:
            self.assertTrue(False, err.args)

    def test_broken_config(self):
        broken_conf = {
            "TIME_LIMIT": 1245,
            "NUM_THREAD": 4,
            "MIN_GAP": 1e-10,
            "BUCKET_SIZE": 4.5,
        }

        with self.assertRaisesRegex(ValueError, "Configuration Error: BUCKET_SIZE"):
            check_config(broken_conf)


if __name__ == "__main__":
    unittest.main()
