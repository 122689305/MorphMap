# cache
import os
import pickle
import time
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
open = open
def cache(filename, func, *args, **keywords):
  from . import Element
  time_start = time.time()
  existed = os.path.isfile(filename)
  print('cache {0}'.format(filename))
  if existed:
    print('loading form {0}'.format(filename))
    cached = open(filename, 'rb')
    data = pickle.load(cached)
  else:
    print('loading by computing')
    data = func(*args, **keywords)
    pickle.dump(data, open(filename, 'wb'))
  print('loading finished :{0}s'.format(time.time()-time_start))
  return data


def clearCache(filename):
  print(filename)
  existed = os.path.isfile(filename)
  if existed:
    os.remove(filename)

