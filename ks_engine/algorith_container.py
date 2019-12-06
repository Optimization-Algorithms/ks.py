#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from .kernel_algorithms import *


class AlgorithContainer:
    """
    """

    def __init__(
        self,
        *,
        kernel_builder=None,
        bucket_builder=None,
        kernel_sort=None,
        bucket_sort=None
    ):
        if kernel_builder:
            self.kernel_builder = kernel_builder
        else:
            self.kernel_builder = kernel_builders.default

        if bucket_builder:
            self.bucket_builder = bucket_builder
        else:
            self.bucket_builder = bucket_builders.default

        if kernel_sort:
            self.kernel_sort = kernel_sort
        else:
            self.kernel_sort = None

        if bucket_sort:
            self.bucket_sort = bucket_sort
        else:
            self.bucket_sort = None
