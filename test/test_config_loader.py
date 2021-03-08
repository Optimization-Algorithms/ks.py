#! /usr/bin/python

import os
import unittest


from ks_engine.config_loader import (
    check_config,
    DEFAULT_CONF,
    get_base_name,
    check_file_parameters,
)


class TestCheckFileParametes(unittest.TestCase):
    def test_correct_config_without_instance(self):
        conf = {
            "INSTANCE": "",
            "DEBUG": "test-run.csv",
            "SOLUTION_FILE": "test-sol.sol",
        }

        check_file_parameters(conf)
        self.assertEqual(conf["INSTANCE"], "")
        self.assertEqual(conf["DEBUG"], "test-run.csv")
        self.assertEqual(conf["SOLUTION_FILE"], "test-sol.sol")

    def test_correct_config_with_instance(self):
        conf = {
            "INSTANCE": "test",
            "DEBUG": "test-run.csv",
            "SOLUTION_FILE": "test-sol.sol",
        }

        check_file_parameters(conf)
        self.assertEqual(conf["INSTANCE"], "test")
        self.assertEqual(conf["DEBUG"], "test-run.csv")
        self.assertEqual(conf["SOLUTION_FILE"], "test-sol.sol")

    def test_correct_config_with_set_output(self):
        conf = {"INSTANCE": "name.mps", "DEBUG": True, "SOLUTION_FILE": True}

        check_file_parameters(conf)
        self.assertEqual(conf["INSTANCE"], "name.mps")
        self.assertEqual(conf["DEBUG"], "name-run.csv")
        self.assertEqual(conf["SOLUTION_FILE"], "name-sol.sol")

        conf = {"INSTANCE": "name.mps", "DEBUG": True, "SOLUTION_FILE": False}

        check_file_parameters(conf)
        self.assertEqual(conf["INSTANCE"], "name.mps")
        self.assertEqual(conf["DEBUG"], "name-run.csv")
        self.assertEqual(conf["SOLUTION_FILE"], None)

    def test_wrong_config(self):
        conf = {"INSTANCE": "", "DEBUG": False, "SOLUTION_FILE": True}

        with self.assertRaisesRegex(
            ValueError,
            "cannot set solution file name without an instance name in config file",
        ):
            check_file_parameters(conf)

    def test_wrong_parameter_type(self):
        conf = {"INSTANCE": "", "DEBUG": "test-run.csv", "SOLUTION_FILE": 56}

        with self.assertRaisesRegex(
            ValueError, "SOLUTION_FILE is expected to be a string or boolean"
        ):
            check_file_parameters(conf)


class TestGetBaseName(unittest.TestCase):
    def test_get_base_name(self):
        sol = get_base_name("instance.mps")
        self.assertEqual(sol, "instance")

        sol = get_base_name("instance")
        self.assertEqual(sol, "instance")

        path_name = os.path.join("instance-dir", "instance.mps")
        sol = get_base_name(path_name)
        self.assertEqual(sol, "instance")

        path_name = os.path.join("instance-dir", "instance")
        sol = get_base_name(path_name)
        self.assertEqual(sol, "instance")


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
            "BUCKET": "Some name",
        }
        corr_conf = {**DEFAULT_CONF, **corr_conf}
        try:
            check_config(corr_conf)
        except ValueError as err:
            self.assertTrue(False, err.args)

    def test_broken_config(self):
        broken_conf = {
            "TIME_LIMIT": 1245,
            "NUM_THREAD": 4,
            "MIN_GAP": 1e-10,
            "BUCKET": 4.5,
            "BUCKET_CONF": {},
        }
        broken_conf = {**DEFAULT_CONF, **broken_conf}
        with self.assertRaisesRegex(ValueError, "Configuration Error: BUCKET"):
            check_config(broken_conf)


if __name__ == "__main__":
    unittest.main()
