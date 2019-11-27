# ks.py


A Python Kernel Search implementation 

## Description

Kernel Search is a matheuristic designed to solve in short time
hard generic MIP problems. It factrize the problem into a smaller 
problems and uses an exact MIP solver to find the optimal to each sub
problem. 

_ks.py_ is pure python Kernel Search implementation, using Gurobi® as black-box solver.
It is a  library (**ks_engine**)that, once installed, is callable 
by any python program. The libray allows to 
define custom callback to create the initial kernel and the buckets.
Otherwise is possible to use one of the general purpose method present in the library. 
The library also contains a configuration loader that can be used 
to configure the solver and the kernel search itself. The configuration loader also support custom entries, so it's possible 
for the client code to use just one configuration file to configure
both the library and the user difined code.


## Installation
work in progress


## Usage

work in progress
