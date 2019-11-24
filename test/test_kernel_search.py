#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

import unittest
from string import ascii_letters, ascii_lowercase, ascii_uppercase

from ks_engine.kernel_search import select_vars, update_kernel
from ks_engine import model
from ks_engine.solution import Solution


class TestBucketSelection(unittest.TestCase):
    def test_select_vars(self):
        kernel, first_bucket = self._make_kernel()
        select_vars(kernel, first_bucket)

        for l in ascii_lowercase:
            self.assertTrue(kernel[l], l)

        for i, l in enumerate(ascii_uppercase):
            if i % 2:
                self.assertFalse(kernel[l], l)
            else:
                self.assertTrue(kernel[l], l)

    def test_update_kernel(self):
        kernel, first_bucket = self._make_kernel()
        select_vars(kernel, first_bucket)
        solution = self._build_solution(first_bucket)
        update_kernel(kernel, first_bucket, solution, 0)

        selected_vars = "".join(l for i, l in enumerate(ascii_letters) if i % 2 == 0)
        tmp = "".join(l for i, l in enumerate(ascii_lowercase) if i % 2 != 0)
        selected_vars += "".join(l for i, l in enumerate(tmp) if i < 4)

        for l in ascii_lowercase:
            if l in selected_vars:
                self.assertTrue(kernel[l], l)
            else:
                self.assertFalse(kernel[l], l)

    def _build_solution(self, bucket):
        gen = ((letter, int(index < 4)) for index, letter in enumerate(bucket))
        return Solution(12, gen)

    def _make_kernel(self):
        kernel = {
            letter: index % 2 == 0
            for index, letter in enumerate(ascii_letters)
        }

        first_bucket = [
            letter for i, letter in enumerate(ascii_lowercase) if i % 2 != 0
        ]
        return kernel, first_bucket


if __name__ == "__main__":
    unittest.main()
