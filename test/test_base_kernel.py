#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>


import unittest 
from string import ascii_lowercase

from ks_engine.kernel_utils.base_kernel import sort_base_variables, percentage_better_kernel_builder
from ks_engine.solution import Solution

def build_kernel():

    kernel = {k: i % 2 == 0 for i, k in enumerate(ascii_lowercase)}
    values = Solution(0.0, ((k, -i) for i, k in enumerate(ascii_lowercase)))

    return kernel, values


class TestKernelSorter(unittest.TestCase):
    def test_kernel_sort(self):
        kernel, values = build_kernel()
        sort_kernel = sort_base_variables(kernel, values)
        self.assertEqual(len(ascii_lowercase) / 2, len(sort_kernel))
        self.assertEqual(sort_kernel, ['y', 'w', 'u', 's', 'q', 'o', 'm', 'k', 'i', 'g', 'e', 'c', 'a'])


class TestKernelBuilder(unittest.TestCase):
    def test_kernel_builder(self):
        kernel, values = build_kernel()
        kernel = percentage_better_kernel_builder(kernel, values, 0.75)
        # 13 * 0.75 = 9.75 -> 9
        self.assertEqual(len(kernel), len(ascii_lowercase))
        count = 0
        for v in kernel.values():
            if v:
                count += 1
        self.assertEqual(count, 9)
        for k in ['y', 'w', 'u', 's', 'q', 'o', 'm', 'k', 'i']:
            self.assertTrue(kernel[k])
                



if __name__ == "__main__":
    unittest.main()

