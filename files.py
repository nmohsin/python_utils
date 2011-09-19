import os, os.path
import sys
import glob

def dirbasename(path):
    "Returns the base name of the directory containing this file."
    return os.path.basename(os.path.dirname(path))


def main():
    # Quick testing code.
    path = '/home/nadeem/code/python/utils/files.py'
    print dirbasename(path)


if __name__ == '__main__':
    main()
