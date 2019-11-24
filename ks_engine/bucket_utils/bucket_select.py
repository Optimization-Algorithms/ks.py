#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>


from .base_bucket import fixed_size_bucket, decresing_size_bucket

BUCKETS = {"fixed": fixed_size_bucket, "decrease": decresing_size_bucket}


def install_bucket_generator(name, function):
    BUCKETS[name] = function


def get_bucket(name):
    return BUCKETS[name]
