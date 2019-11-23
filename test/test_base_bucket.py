#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

import unittest

from string import ascii_letters
from secrets import randbelow

from ks_engine.bucket_utils.base_bucket import fixed_size_bucket, get_bucket_variables, decresing_size_bucket
from ks_engine.model import Variable


def build_kernel():
    kernel = {
        k: Variable(randbelow(10 * len(ascii_letters)), i % 2 == 0)
        for i, k in enumerate(ascii_letters)
    }
    return kernel


class TestBucketSorting(unittest.TestCase):
    def test_sorter(self):
        kernel = build_kernel()
        bucket_vars = get_bucket_variables(kernel)
        self.assertEqual(len(bucket_vars), len(ascii_letters) // 2)

        prev = None
        for var in bucket_vars:
            if prev:
                self.assertLessEqual(prev, kernel[var].value)
            prev = kernel[var].value


class TestBaseBucket(unittest.TestCase):
    def test_buckets_correct_size(self):
        """
        in this test the bucket size 
        is a divisor of number of variables
        out of the kernel
        """

        config = {"size": 13}
        count = 0
        kernel = build_kernel()
        for bucket in fixed_size_bucket(kernel, **config):
            count += 1
            self.assertEqual(len(bucket), config["size"])
        self.assertEqual(count, 2)

    def test_buckets_wrong_size(self):
        """
        in this test the bucket size 
        is NOT a divisor of number of variables
        out of the kernel
        """

        config = {"size": 10}
        sizes = [10, 10, 6]
        kernel = build_kernel()
        buckets = fixed_size_bucket(kernel, **config)
        for bucket, length in zip(buckets, sizes):
            self.assertEqual(len(bucket), length)


class TestVariableSizeBucket(unittest.TestCase):
    def test_buckets_correct_size(self):
        config = {"count": 2}
        count = 0
        kernel = {k: Variable(randbelow(100), False) for k in range(9)}
        sizes = [6, 3]
        for bucket, length in zip(decresing_size_bucket(kernel, **config), sizes):
            count += 1
            self.assertEqual(len(bucket), length)
        self.assertEqual(count, 2)


    def test_buckets_wrong_size(self):
        config = {"count": 2}
        count = 0
        kernel = {k: Variable(randbelow(100), False) for k in range(10)}
        sizes = [6, 3, 1]
        for bucket, length in zip(decresing_size_bucket(kernel, **config), sizes):
            count += 1
            self.assertEqual(len(bucket), length)
        self.assertEqual(count, 3)  

if __name__ == "__main__":
    unittest.main()
