#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>


from .base_bucket import fixed_size_bucket, decresing_size_bucket

BUCKETS = {"fixed": fixed_size_bucket, "decrease": decresing_size_bucket}


def install_bucket_generator(name, function):
    """
    Add a new bucket generator to the available bucket generators

    Parameters
    ----------
    name : str
        Bucket generator name. 
    
    function: callable
        Bucket generator function

    """
    BUCKETS[name] = function


def get_bucket(name):
    """
    GEt a  bucket generator from the available bucket generators

    Parameters
    ----------
    name : str
        Bucket generator name. 


    Raises
    ------
    KeyError
        if name does not point to an available bucket generator


    Returns
    -------
    bucket_builder : callable
        a callable able to partition 
        variable outside the initial kernel 
        into buckets
    """
    return BUCKETS[name]
