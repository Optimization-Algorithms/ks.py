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
        """
        Extends the debug informations.

        :param data: the new data to be added.
        :param index: the index of the new data to be added.
        """
        self.store[index] = data

        if self.max_bucket < index.bucket:
            self.max_bucket = index.bucket

        if self.max_iter < index.iteration:
            self.max_iter = index.iteration

    def export_csv(self, file_name: str, compress):
        """
        Save as a csv file the current debug information in csv format.

        :param file_name: the name of the file whera save data.
        :type file_name: str
        :param compress: determine if the csv must be compressed in gz.
        :type compress: bool
        """
        csv = self.get_csv()
        if compress:
            csv = bytes(csv, "UTF-8")
            with gzip.open(file_name, "wb") as file:
                file.write(csv)
        else:
            with open(file_name, "w") as file:
                file.write(csv)

    def get_csv(self):
        """
        Returns the current debug information in csv format.

        :return: a string representing the csv file.
        :rtype: str
        """
        out = "bucket,iteration,value,time,nodes,kernel_size,bucket_size"
        for k, v in self.store.items():
            tmp = f"{k.bucket},{k.iteration},{v.value},{v.time},{v.nodes},{v.kernel_size},{v.bucket_size}"
            out += "\n" + tmp
        return out

    def bucket_iter(self, iteration):
        """
        Yields information relative to a particular iteration.

        :param iteration: the iteration whose information are of interest.
        :yield: a bucket-value pair from all the stored ones.
        """
        for k, v in self.store.items():
            if k.iteration == iteration:
                yield k.bucket, v

    def iteration_iter(self, bucket):
        """
        Yields information relative to a particular bucket.

        :param bucket: the bucket whose information are of interest.
        :yield: a iteration-value pair from all the stored ones.
        """
        for k, v in self.store.items():
            if k.bucket == bucket:
                yield k.iteration, v

    def full_iter(self):
        """
        Yields name-value pair of debug informations.

        :yield: a name-value pair from all the stored ones.
        """
        for k, v in self.store.items():
            yield k, v


class Solution:
    def __init__(self, value, var_iter):
        self.vars = {k: v for k, v in var_iter}
        self.value = value
        self.debug = DebugInfo()

    def get_value(self, name):
        """
        Returns the value associated with a var name.

        :param name: the name of the variable whose value is searched.
        :return: the value of the variable.
        """
        return self.vars[name]

    def update(self, value, var_iter):
        """
        Update the value and variable values of the current solution.

        :param value: value of the objective function.
        :param var_iter: list of var-value pair.
        """
        self.value = value
        for k, v in var_iter:
            self.vars[k] = v

    def update_debug_info(self, index, debug_info):
        """
        Extends data to the debug of the run.

        :param index: the index in a dict where the new info will be saved.
        :param debug_info: the information to store.
        """
        self.debug.add_data(debug_info, index)

    def variables(self):
        """
        Returns the variables values.

        :return: A numpy array representing the values
        :rtype: numpy.array
        """
        vals = self.vars.values()
        list_vals = list(vals)
        return np.array(list_vals)

    def save_as_sol_file(self, file_name: str):
        """
        Save persinstently the solution.

        :param file_name: the name of the file.
        """
        file_name = get_solution_file_name(file_name)

        with open(file_name, "w") as file:
            for k, v in self.vars.items():
                print(k, v, file=file)


def get_solution_file_name(file_name):
    """
    Return the name of the file in which save the solution

    :param file_name: the name of the file.
    :return: A .sol filename
    :rtype: str
    """
    if file_name is None:
        return None

    if file_name.endswith('.sol'):
        return file_name
    else:
        return f"{file_name}.sol"
