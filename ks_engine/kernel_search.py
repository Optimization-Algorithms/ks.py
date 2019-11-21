#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from .model import Model





def init_kernel(mps_file, config):
    lp_model = Model(mps_file, config, True)
    if not lp_model.run():
        raise ValueError(f'Given Problem: {mps_file} has no LP solution')
    base_kernel = lp_model.get_variables()

    int_model = Model(mps_file, config, False)
    int_model.disable_variables(base_kernel)
    if not int_model.run():
        raise ValueError(f'Given Problem: {mps_file} has no Initial reduction solution')

    return int_model.build_solution()






def kernel_search(mps_file, config):
    return init_kernel(mps_file, config)