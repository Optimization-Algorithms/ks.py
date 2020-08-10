
import numpy as np
import sklearn as sk

from .model import Model

def init_feature_kernel(mps_file, config, kernel_builder, kernel_sort):
    
    preload_model = Model(mps_file, config, False)
    count = config['COUNT']
    groups = config['GROUPS']
    if rel_size := config['REL_SIZE']:
        model_size = preload_model.model_size()
        abs_size = int(model_size * rel_size)
    else:
        abs_size = config['ABS_SIZE']


    for var in preload_model.model.getVars():
        print(var.varName)

    exit()

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



