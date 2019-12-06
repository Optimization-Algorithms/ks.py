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
At the current time there is not any installation script or packages. In any 
case, in order to work with *ks_engin* is mandatory to install the dependencies 
using

```bash
[sudo] pip install requirements.txt
```
It is also required to globally install the latest Gurobi version. 

### Tests
It's possible to test the code using, in the project 
root directory

```bash
python -m pytest
```

Those test does not includes tests for the solver API,
so it's possible to run tests in a CI environment. Also the solver should be correct. 

## Usage

This library can be used out of the box or can be extended to support new algorithms to sort variables, build the base kernel and build the buckets.

* [Direct Usage](base_usage.md)
* [Extension] (extension.md)
