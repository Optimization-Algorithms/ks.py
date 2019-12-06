#! /usr/bin/python


# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>


def kernel_sort(kernel: dict, values):
    tmp = [k for k, v in kernel.items() if v]
    tmp.sort(key=lambda x: values.get_value(x))
    return tmp


def bucket_sort(kernel: dict, values):
    tmp = [k for k, v in kernel.items() if not v]
    tmp.sort(key=lambda x: -values.get_value(x))
    return tmp


KERNEL_SORTERS = {
    "base_kernel_sort": kernel_sort,
}

BUCKET_SORT = {
    "base_bucket_sort": bucket_sort,
}
