## Doc building

To build the doc are necessary some additional packages. These can be installed e.g. with pip:

```
pip install sphinx
pip install sphinx_rtd_theme
```

A good practice is to install these package locally (with --user) or in a virtualenv (venv). Anyway, it's not mandatory.

If the build of the doc is make locally it's strongly recommended to create a separete folder inside
the sphinx_doc folder, let's call this new folder build.

To build the doc as a html "website" from the sphinx_doc folder:

```
sphinx-build source build
```

In this way, the resulting "website" will be in the build folder. Be free to change the destination folder name.
