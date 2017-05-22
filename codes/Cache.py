# cache
def cache(filename, func, *args, **keywords):
	import os
	existed = os.path.isfile(filename)
	if existed:
		cached = open(filename, 'rb')
		return pickle.load(cached)
	else:
		data = func(*args, **keywords)
		pickle.dump(data, open(filename, 'wb'))
		return data

def clearCache(filename):
	import os
	existed = os.path.isfile(filename)
	if existed:
		os.remove(filename)

