#! /usr/bin/python


# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>
# Modified in 2020 by Marco De Ramundo

import numpy as np

# support function for cheb sort


def cheb_nodes(n: int):
    tmp = []
    for num in range(1, n):
        t = np.cos((2 * num - 1) * np.pi / (2 * n))
        if t < 0:
            t += 1
        tmp.append(t)
    return tmp


def kernel_sort(kernel: dict, values):
    tmp = [k for k, v in kernel.items() if v]
    tmp.sort(key=lambda x: values.get_value(x))
    return tmp


def bucket_sort(kernel: dict, values):
    tmp = [k for k, v in kernel.items() if not v]
    tmp.sort(key=lambda x: -values.get_value(x))
    return tmp


def cheb_sort(kernel: dict, values):
    tmp = [k for k, v in kernel.items() if not v]
    tmp.sort(key=lambda x: -values.get_value(x))
    np.split(tmp, 2)  # divide la lista in due sottoliste
    sup_ls = cheb_nodes(len(tmp))  # crea i nodi di cheb con due subarray
    np.split(sup_ls, 2)
    sorted = []  # analisi dei nodi e riordino della lista
    j, k = 0, 0
    for _ in range(1, len(tmp)):
        if sup_ls[0][j] < sup_ls[1][k]:
            sorted.append(sup_ls[1][k])
            k += 1
        else:
            sorted.append(sup_ls[0][j])
            j += 1
    return sorted


KERNEL_SORTERS = {
    "base_kernel_sort": kernel_sort,
}

BUCKET_SORT = {
    "base_bucket_sort": bucket_sort,
    "cheb_bucket_sort": cheb_sort,
}
