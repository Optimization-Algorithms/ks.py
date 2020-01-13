#! /usr/bin/python

import unittest

from secrets import randbelow
from tempfile import TemporaryDirectory
from os import path
import gzip
from ks_engine.solution import DebugInfo, DebugData, DebugIndex


class BaseTest(unittest.TestCase):
    def get_random_data(self, count):
        out = []
        for _ in range(count):
            data = DebugData(
                randbelow(100),
                randbelow(100),
                randbelow(100),
                randbelow(100),
                randbelow(100),
            )
            out.append(data)
        return out

    def test_storage(self):
        buckets = 20
        store = DebugInfo()
        iter_one = self.get_random_data(buckets)
        for i, d in enumerate(iter_one):
            index = DebugIndex(0, i)
            store.add_data(d, index)

        iter_two = self.get_random_data(buckets)
        for i, d in enumerate(iter_two):
            index = DebugIndex(1, i)
            store.add_data(d, index)

        # test bucket iteration
        for i in range(buckets):
            data = [iter_one[i], iter_two[i]]
            for k, v in store.iteration_iter(i):
                self.assertEqual(data[k], v)

        for k, v in store.bucket_iter(0):
            self.assertEqual(iter_one[k], v)

        for k, v in store.bucket_iter(1):
            self.assertEqual(iter_two[k], v)

    def build_base_export(self):
        store = DebugInfo()

        data = DebugData(1, 1, 1, 1, 1)
        index = DebugIndex(0, 0)
        store.add_data(data, index)

        data = DebugData(1, 1, 1, 1, 1)
        index = DebugIndex(0, 1)
        store.add_data(data, index)

        expected = "bucket, iteration, value, time, nodes, kernel_size, bucket_size\n0, 0, 1, 1, 1, 1, 1\n1, 0, 1, 1, 1, 1, 1"

        return store, expected

    def test_export(self):
        store, expected = self.build_base_export()
        csv = store.get_csv()

        self.assertEqual(csv, expected)

    def test_file_export(self):
        store, expected = self.build_base_export()
        with TemporaryDirectory() as tmp_root:
            file = path.join(tmp_root, "debug.csv")
            store.export_csv(file, False)
            with open(file, "r") as data:
                self.assertEqual(data.read(), expected)

    def test_compressed_file_export(self):
        store, expected = self.build_base_export()
        with TemporaryDirectory() as tmp_root:
            file = path.join(tmp_root, "debug.csv.gz")
            store.export_csv(file, True)
            with gzip.open(file, "r") as data:
                read = data.read().decode()
                self.assertEqual(read, expected)


if __name__ == "__main__":
    unittest.main()
