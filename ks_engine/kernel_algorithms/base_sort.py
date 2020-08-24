#! /usr/bin/python


# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>
# Modified in 2020 by Marco De Ramundo

import numpy as np

# support function for cheb sort


def cheb_nodes(count: int):
    output = [0] * count
    for i, n in enumerate(range(1, count + 1)):
        tmp = (((2 * n) - 1) / (2 * count)) * np.pi 
        t = np.cos(tmp)
        if t < 0:
            t += 1
        output[i] = t
    return np.array(output)


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
    tmp = np.array(tmp)
    head, tail = np.array_split(tmp, 2) 
    nodes = cheb_nodes(len(tmp)) 
    head_nodes, tail_nodes = np.split(nodes, 2)
    output = []
    j, k = 0, 0
    
    for _ in range(len(tmp)):
        done_tail = k >= len(tail_nodes)
        done_head = j >= len(head_nodes)
        if done_tail:
            flag = True 
        elif done_head:
            flag = False  
        else:
            if head_nodes[j] < tail_nodes[k]:
                flag = False
            else:
                flag = True
            
        if flag:
            output.append(head[j])
            j += 1
        else:
            output.append(tail[k])
            k += 1
        
        
    return output


KERNEL_SORTERS = {
    "base_kernel_sort": kernel_sort,
}

BUCKET_SORT = {
    "base_bucket_sort": bucket_sort,
    "cheb_bucket_sort": cheb_sort,
}
