#! /usr/bin/env python
# utils/files.py

"""This module provides convenience functions for manipulating and extracting information from
filenames and directory names. 
"""

import os, os.path

def parent(path):
    "Returns the parent directory of the specified file."
    return os.path.dirname(path)

def filename(path):
    "Returns the file in this path."
    d, f = os.path.split(path)
    return f

def parent_basename(path):
    "Returns the name of the directory containing this file."
    return os.path.basename(os.path.dirname(path))

def parents(path_list):
    """Returns the directory names of a list of file paths.

    For situations where directory names contain useful information.
    """
    return [os.path.dirname(path) for path in path_list]

def parent_basenames(path_list):
    "Similar to parents, but returns directory base names instead."
    return [parent_basename(path) for path in path_list]

def filenames(path_list):
    """Returns the file names of every file in a list of file paths.

    For situations where the file name contains useful information.
    """
    return [filename(path) for path in path_list]

def make_new_name(path, new_dir=None, new_ext=None):
    """Transforms the given path (to a file) by changing the directory and file extension.

    Leaving out either optional argument will leave the relevant part of the path unchanged in the
    returned path.
    """
    fpath, fext = os.path.splitext(path)
    fdir, fname = os.path.split(fpath)
    if new_dir:
        fdir = new_dir
    if new_ext:
        fext = new_ext
    return os.path.join(fdir, fname + fext)

def with_new_extension(path, new_ext):
    "Returns the path with a changed extension."
    return make_new_name(path, new_ext=new_ext)

def with_new_parent(path, new_dir):
    "Returns the path after changing the parent directory."
    return make_new_name(path, new_dir=new_dir)
