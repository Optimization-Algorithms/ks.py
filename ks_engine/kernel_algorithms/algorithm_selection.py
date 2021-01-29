#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from .base_bucket import BUCKET_BUILDERS, fixed_size_bucket
from .base_kernel import KERNEL_BUILDERS, base_kernel_builder
from .base_sort import *


class Selector:

    """
    Selector allows client code to safely choose between available
    algorithms.
    """

    def __init__(self, base_store, default):
        """
        Parameters
        ----------
        base_store: dict
            a dictionary mapping string into functions

        default: function
            the default function between the available ones

        """
        self.store = base_store
        self.default = default

    def add_algorithm(self, name, function):
        """
        Insert a new algorithm in the store, if not present

        Parameters
        ----------
        name: str
            new algorithm name, must be different from
            the corrently available
        function: callable
            the algorithm implementation, although not required it
            must have the same signature of the order functions

        Raises
        ------
            ValueError if name is already pointing to a function

        """
        try:
            self.store[name]
        except KeyError:
            self.store[name] = function
        else:
            raise ValueError(f"algorithm {name} is already installed")

    def get_algorithm(self, name):
        """
        Return the algorithm pointed by given name

        Parameters
        ----------
            name: str
                desidered method name

        Returns
        -------
            the function associated to the given name if
            it is available, None otherwise.
        """
        return self.store.get(name)


bucket_builders = Selector(BUCKET_BUILDERS, fixed_size_bucket)
kernel_builders = Selector(KERNEL_BUILDERS, base_kernel_builder)

kernel_sorters = Selector(KERNEL_SORTERS, kernel_sort)
bucket_sorters = Selector(BUCKET_SORT, bucket_sort)
