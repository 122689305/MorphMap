# coding=utf-8
import pickle
import subprocess
import re
import json

class MapBuilder:
  server_url = 'http://202.120.38.146:7998/data/sparql'
  cache_dir = '../cache'
  deep_level = 1

  # return (status,data)
  # status: 0 or other
  # data: json-like object
  def rawQuery(self, resource):
    o = (status, data) = subprocess.getstatusoutput("s-query --service={0} 'select ?y ?z where {{<{1}> ?y ?z}}'".format(self.server_url, resource))
    return o 

  # return (status, empty, data)
  # status: 404 or 200
  # empty: Ture if the content of data is empty
  # data: a list of tuples. each tuple is in the form of (property, value)
  def query(self, name):
    (status, data) = self.rawQuery('http://zh.dbpedia.org/resource/'+name)
    if (status == 0):
      jo = json.loads(data)
      data = map(lambda yz: (yz['y']['value'].split('/')[-1], yz['z']['value'] if yz['z']['type'] != 'uri' else yz['z']['value'].split('/')[-1]), jo['results']['bindings'])
      data = list(data)
      return ('200', len(data)==0, data)
    else:
      return ('400', True, None)

  # return (status, empty, data)
  # status: 404 or 200
  # empty: Ture if the content of data is empty
  # data: a list of tuples. each tuple is in the form of (property, value). values are splited from original value
  def fullQuery(self, name):
    (status, empty, data) = self.query(name)
    if empty:
      return (status, empty, [])
    flat = lambda L: sum(list(map(flat,L)),[]) if isinstance(L,list) else [L]
    data = map(lambda tup: [(tup[0], entity) for entity in self.entitiesOf(tup[1])], data)
    data = list(data)
    data = flat(data)
    return (status, empty, data)

  def _fullQuery(self, name):
    return self.fullQuery(name)[2]

  # return [w1, w2, ...]
  # word segmentation. split in to queryful names
  def entitiesOf(self, literal):
    return re.split(r"[：\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）!\"#$%&\'()*+,-./:;<=>?@\[\\\]\^_`{|}~]+",literal)

  # return a json-like object
  # it defines a directed tree
  def buildMap(self, name):
    def _buildMap(name):
      data = (name, self._fullQuery(name))
      for i in range(self.deep_level):
        expand = lambda t: (t[0] ,list(map(expand, t[1]))) if isinstance(t[1], list) else (t[0], (t[1], self._fullQuery(t[1])))
        data = expand(data)
      return data
    return self.cache(name, _buildMap)
  
  # cache
  def cache(self, name, func):
    import os
    filename = os.path.join(self.cache_dir, name)
    existed = os.path.isfile(filename)
    if existed:
      cached = open(filename, 'rb')
      return pickle.load(cached)
    else:
      data = func(name)
      pickle.dump(data, open(filename, 'wb'))
      return data

if __name__ == '__main__':
  mapBuilder = MapBuilder()
  mapBuilder.deep_level = 1
  q = mapBuilder.buildMap('薄熙来')
  print(q)
