#! /usr/bin/env python
# utils/sorting.py

"""This module provides common sorting functionality for a variety of structures.
"""
import os, os.path
import files

def by_size(paths, reverse=False):
    "Sorts a list of files/folders by their sizes."
    return [filename for filename, filesize in
            sorted([(path, files.getsize(path)) for path in paths],
                   key=lambda (f, s) : s, reverse=reverse)]


def dict_by_value(adict, reverse=False):
    """Returns the entries of a dictionary as list of key-value tuples, sorted by value.

    This is similar to the standard sorting order of nltk.FreqDist.
    """
    return [(key, value) for key, value in
            sorted(adict.iteritems(), key=lambda (k, v) : (v, k), reverse=reverse)]
