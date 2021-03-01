#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from .base_bucket import BUCKET_BUILDERS, fixed_size_bucket
from typing import Callable
from .base_kernel import KERNEL_BUILDERS, base_kernel_builder
from .base_sort import kernel_sort, bucket_sort, BUCKET_SORT, KERNEL_SORTERS


class Selector:
    """
    Selector allows client code to safely choose between available
    algorithms.

    :param base_store: a dictionary mapping string into functions
    :type base_store: dict
    :param default: the default function between the available ones
    :type default: Callable
    """
    def __init__(self, base_store: dict, default: Callable):
        self.store = base_store
        self.default = default

    def add_algorithm(self, name: str, function: Callable):
        """
        Insert a new algorithm in the store, if not present

        :param name: new algorithm name, must be different from
            the corrently available
        :type name: str
        :param function: the algorithm implementation, although not required it
            must have the same signature of the order functions
        :type function: Callable
        :raises ValueError: if name is already pointing to a function
        """
        try:
            self.store[name]
        except KeyError:
            self.store[name] = function
        else:
            raise ValueError(f"algorithm {name} is already installed")

    def get_algorithm(self, name: str):
        """
        Return the algorithm pointed by given name

        :param name: desidered method name
        :type name: str
        :return: the function associated to the given name if
            it is available, None otherwise.
        :rtype: Callable
        """
        return self.store.get(name)


bucket_builders = Selector(BUCKET_BUILDERS, fixed_size_bucket)
kernel_builders = Selector(KERNEL_BUILDERS, base_kernel_builder)

kernel_sorters = Selector(KERNEL_SORTERS, kernel_sort)
bucket_sorters = Selector(BUCKET_SORT, bucket_sort)
