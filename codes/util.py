import time

def showComputingTime(f):
  def __call__(*args, **kwargs):
    time_start = time.time()
    print('computing {0}'.format(f.__name__))
    data = f(*args, **kwargs)
    print('computed {0}: {1}s'.format(f.__name__, time.time() - time_start))
    return data
  return __call__
