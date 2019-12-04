#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>


import unittest

from ks_engine.kernel_algorithms.algorithm_selection import Selector


class TestSelector(unittest.TestCase):

    def test_selector(self):
        sel = Selector({'a': 1, 'b':2, 'c': 3}, 4)

        self.assertEqual(sel.default, 4)
        self.assertEqual(sel.get_algorithm('a'), 1)

        self.assertIsNone(sel.get_algorithm('f'))
        sel.add_algorithm('f', -3)
        self.assertEqual(sel.get_algorithm('f'), -3)

        with self.assertRaisesRegex(ValueError, "algorithm a is already installed"):
            sel.add_algorithm('a', 34)



if __name__ == "__main__":
    unittest.main()