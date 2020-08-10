
import numpy as np
import sklearn as sk

import secrets

from .model import Model

def init_feature_kernel(mps_file, config, kernel_builder, kernel_sort):
    
    preload_model = Model(mps_file, config, False)
    model_count = config['COUNT']
    group_count = config['GROUPS']
    if rel_size := config['REL_SIZE']:
        model_size = preload_model.model_size()
        abs_size = int(model_size * rel_size)
    else:
        abs_size = config['ABS_SIZE']

    var_names = get_var_names(preload_model)
    for k in range(model_count):
        selected = select_random_vars(var_names, abs_size)
        solve_model(mps_file, selected)



    #groups = build_groups(get_var_names(preload_model), group_count)

def solve_model(mps_file, config, selected_vars):
    lin_model = Model(mps_file, config, True)
    lin_model.disable_variables(selected_vars)
    lin_model.run()


def select_random_vars(var_names, count):
    selection = np.random.choice(var_names, size=count, replace=False)
    selected = set(selection)
    for var in var_names:
        if var not in selected:
            yield var, None
    

def build_groups(var_names, groups):
    var_count = len(var_names)
    group_size = len(var_names) // groups
    if var_count % groups:
        group_size += 1
    begin = 0
    output = [None] * groups   
    for i in range(groups):
        output[i] = var_names[begin: begin + group_size]
        begin += group_size



    return output

def get_var_names(model):
    return [var.varName for var in model.model.getVars()]



