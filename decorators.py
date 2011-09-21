#! /usr/bin/env python
#! utils/decorators.py

"""This module provides useful decorators."""

import functools
import time

class memoized(object):
   """Decorator that caches a function's return value each time it is called.

   If called later with the same arguments, the cached value is returned, and
   not re-evaluated.
   """
   def __init__(self, func):
      self.func = func
      self.cache = {}

   def __call__(self, *args):
      try:
         return self.cache[args]
      except KeyError:
         value = self.func(*args)
         self.cache[args] = value
         return value
      except TypeError:
         # uncachable -- for instance, passing a list as an argument.
         # Better to not cache than to blow up entirely.
         return self.func(*args)

   def __repr__(self):
      """Return the function's docstring."""
      return self.func.__doc__

   def __get__(self, obj, objtype):
      """Support instance methods."""
      return functools.partial(self.__call__, obj)

   
def timed(func):
    def timed_wrapper(*args, **kw):
        t = -time.time()
        result = func(*args, **kw)
        t += time.time()
        
        print '%r completed execution in %2.2f sec' % (func.__name__, t)
        return result
    return timed_wrapper
