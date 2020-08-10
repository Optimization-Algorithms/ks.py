#! /usr/bin/python

import unittest

from ks_engine.feature_kernel import build_groups


class TestBuildGroups(unittest.TestCase):
    
    def test_build(self):
        var_names = list(range(100))
        group_count = 10
        group_size = len(var_names) // group_count
        groups = build_groups(var_names, group_count)
        self.assertEqual(len(groups), group_count)
        for group in groups:
            self.assertEqual(len(group), group_size)



    def test_non_divisible_build(self):
        var_names = list(range(101))
        group_count = 10
        group_size = len(var_names) // group_count
        groups = build_groups(var_names, group_count)
        self.assertEqual(len(groups), group_count)
        for group in groups[:-1]:
            self.assertEqual(len(group), group_size + 1)

        last_size = len(var_names) - ((group_size + 1) * (group_count - 1))
        self.assertEqual(last_size, len(groups[-1]))



if __name__ == '__main__':
    unittest.main()




