#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

import unittest

from string import ascii_letters
from secrets import randbelow

from ks_engine.kernel_algorithms.base_bucket import (
    fixed_size_bucket,
    decresing_size_bucket,
)
from ks_engine.kernel_algorithms.base_sort import bucket_sort, cheb_sort
from ks_engine.solution import Solution

def build_kernel_fixed_size():
    kernel = {k: i % 2 == 0 for i, k in enumerate(ascii_letters)}
    values = Solution(0, ((k, randbelow(100)) for k in ascii_letters))
    return kernel, values


class TestChebSort(unittest.TestCase):
    def test_cheb_sort(self):
        kernel, values = build_kernel_fixed_size()
        vals = cheb_sort(kernel, values)
        
        
class TestBucketSorting(unittest.TestCase):
    def test_sorter(self):
        kernel, values = build_kernel_fixed_size()
        bucket_vars = bucket_sort(kernel, values)
        self.assertEqual(len(bucket_vars), len(ascii_letters) // 2)

        prev = None
        for var in bucket_vars:
            if prev:
                self.assertGreaterEqual(prev, values.get_value(var))
            prev = values.get_value(var)


class TestBaseBucket(unittest.TestCase):
    def test_buckets_correct_size(self):
        """
        in this test the bucket size 
        is a divisor of number of variables
        out of the kernel
        """

        config = {"size": 13}
        count = 0
        kernel, values = build_kernel_fixed_size()
        for bucket in fixed_size_bucket(kernel, values, bucket_sort, {}, **config):
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
        kernel, values = build_kernel_fixed_size()
        buckets = fixed_size_bucket(kernel, values, bucket_sort, {}, **config)
        for bucket, length in zip(buckets, sizes):
            self.assertEqual(len(bucket), length)

    def test_bucket_correct_size_fixed_count(self):
        config = {"count": 13}
        size = 2
        count = 0
        kernel, values = build_kernel_fixed_size()
        buckets = fixed_size_bucket(kernel, values, bucket_sort, {}, **config)
        for bucket in buckets:
            count += 1
            self.assertEqual(len(bucket), 2)

        self.assertEqual(count, 13)

    def test_bucket_wrong_size_fixed_count(self):
        config = {"count": 5}
        sizes = [5, 5, 5, 5, 5, 1]
        count = 0
        kernel, values = build_kernel_fixed_size()
        buckets = fixed_size_bucket(kernel, values, bucket_sort, {}, **config)
        for bucket, size in zip(buckets, sizes):
            count += 1
            self.assertEqual(len(bucket), size)

        self.assertEqual(count, len(sizes))


class TestVariableSizeBucket(unittest.TestCase):
    def test_buckets_correct_size(self):
        config = {"count": 2}
        count = 0
        kernel = {k: False for k in range(9)}
        values = Solution(0.0, ((k, randbelow(100)) for k in range(9)))
        sizes = [6, 3]
        for bucket, length in zip(
            decresing_size_bucket(kernel, values, bucket_sort, {}, **config), sizes
        ):
            count += 1
            self.assertEqual(len(bucket), length)
        self.assertEqual(count, 2)

    def test_buckets_wrong_size(self):
        config = {"count": 2}
        count = 0
        kernel = {k: False for k in range(10)}
        values = Solution(0.0, ((k, randbelow(100)) for k in range(10)))
        sizes = [6, 3, 1]
        for bucket, length in zip(
            decresing_size_bucket(kernel, values, bucket_sort, {}, **config), sizes
        ):
            count += 1
            self.assertEqual(len(bucket), length)
        self.assertEqual(count, 3)


if __name__ == "__main__":
    unittest.main()
