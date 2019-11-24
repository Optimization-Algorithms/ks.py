#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from .base_kernel import base_kernel_builder, percentage_better_kernel_builder

KERNELS = {
    "base": base_kernel_builder,
    "percent best": percentage_better_kernel_builder,
}


def install_kernel_builder(name, function):
    """
    Add a new kernel generator to the available kernel generators

    Parameters
    ----------
    name : str
        Kernel generator name. 
    
    function: callable
        Kernel generator function

    """
    KERNELS[name] = function


def get_kernel_builder(name):
    """
    Get a  kernel generator from the available kernel generators

    Parameters
    ----------
    function: callable
        Kernel generator function

    Raises
    ------
    KeyError
        if name does not point to an available kernel generator


    Returns
    -------
    kernel_builder : callable
        a callable able to select variables
        to put inside the initial kernel

    """
    return KERNELS[name]
