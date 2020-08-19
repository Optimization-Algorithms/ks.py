#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from collections import namedtuple
import gzip

import numpy as np

DebugData = namedtuple(
    "DebugData", ["value", "time", "nodes", "kernel_size", "bucket_size"]
)
DebugIndex = namedtuple("DebugIndex", ["iteration", "bucket"])


class DebugInfo:
    def __init__(self):
        self.store = {}
        self.max_bucket = 0
        self.max_iter = 0

    def add_data(self, data, index):
        self.store[index] = data

        if self.max_bucket < index.bucket:
            self.max_bucket = index.bucket

        if self.max_iter < index.iteration:
            self.max_iter = index.iteration

    def export_csv(self, file_name, compress):
        csv = self.get_csv()
        if compress:
            csv = bytes(csv, "UTF-8")
            with gzip.open(file_name, "wb") as file:
                file.write(csv)
        else:
            with open(file_name, "w") as file:
                file.write(csv)

    def get_csv(self):
        out = "bucket,iteration,value,time,nodes,kernel_size,bucket_size"
        for k, v in self.store.items():
            tmp = f"{k.bucket},{k.iteration},{v.value},{v.time},{v.nodes},{v.kernel_size},{v.bucket_size}"
            out += "\n" + tmp
        return out

    def bucket_iter(self, iteration):
        for k, v in self.store.items():
            if k.iteration == iteration:
                yield k.bucket, v

    def iteration_iter(self, bucket):
        for k, v in self.store.items():
            if k.bucket == bucket:
                yield k.iteration, v

    def full_iter(self):
        for k, v in self.store.items():
            yield k, v


class Solution:
    def __init__(self, value, var_iter):
        self.vars = {k: v for k, v in var_iter}
        self.value = value
        self.debug = DebugInfo()

    def get_value(self, name):
        return self.vars[name]

    def update(self, value, var_iter):
        self.value = value
        for k, v in var_iter:
            self.vars[k] = v

    def update_debug_info(self, index, debug_info):
        self.debug.add_data(debug_info, index)

    def variables(self):
        vals = self.vars.values()
        list_vals = list(vals)
        return np.array(list_vals)
