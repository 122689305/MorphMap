# coding=utf-8
import sys
sys.path.append('../../')
import pickle
import subprocess
import re
import json
from codes import jieba
from codes.zhtools.langconv import *
from codes.GraphStatistics.AliasStatistics import AliasStatistics

class MapBuilder:
  server_url = 'http://202.120.38.146:9600/data/sparql'
  cache_dir = '../cache'
  deep_level = 1
  relations = {'sub_entity':'MapBuilder:sub_entity'}
  stat_data = [(a_sts.count(), a_sts.ea2ae()) for a_sts in [AliasStatistics()]][0][1]

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
      return data
    else:
      return []

  # return (status, empty, data)
  # status: 404 or 200
  # empty: Ture if the content of data is empty
  # data: a list of tuples. each tuple is in the form of (property, value). values are splited from original value
  def fullQuery(self, name):
    data = self.query(name)
    if len(data) == 0:
      return []
    flat = lambda L: sum(list(map(flat,L)),[]) if isinstance(L,list) else [L]
    data = flat(list(map(lambda tup: [(tup[0], entity) for entity in self.entitiesOf(tup[1])], data)))
    return data

  def _fullQuery(self, name):
    print(name)
    return self.fullQuery(name)

  # return [w1, w2, ...]
  # word segmentation. split in to queryful names
  def entitiesOf(self, literal):
    literal =  Converter('zh-hans').convert(literal)
    flat = lambda L: sum(list(map(flat,L)),[]) if isinstance(L,list) else [L] 
    if literal:
      #sep = re.split(r"[：\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）!\"#$%&\'()*+,-./:;<=>?@\[\\\]\^_`{|}~\s]+",literal)
      #return flat(list(list(map(lambda x: list(jieba.cut(x)), sep)) + sep)) 
      e_list = list(jieba.cut(literal))
      e_list = list(filter(lambda e: e != '', e_list))
      return e_list
    else:
      return [literal]

  def getOneHop(self, ex):
    '''
    :parameter ex: entity x. just pass the name of this entity
    :return: (name, flat[ey, explode(ey), a2e(comb(explode(ey)))])
    '''
    from codes.GraphStatistics.AliasStatistics import AliasStatistics
    flat = lambda L: sum(list(map(flat,L)),[]) if isinstance(L,list) else [L]
  
    noEm = lambda e_list: list(filter(lambda e: e != '', e_list))
    noEx = lambda e_list: list(filter(lambda e: e != ex, e_list))
    noInvalidSubE = lambda hopped_e_list: list(filter(lambda hopped_e: len(hopped_e[1]) != 0, hopped_e_list)) 
    explode = lambda e: self.entitiesOf(e)
    # redirects should be detected in GraphMatcher
    comb = lambda e_list: [ [e_list[0]] + l for l in comb(e_list[1:])] + comb(e_list[1:]) if len(e_list) > 1 else [ [e_list[0]], [] ]
    join_comb = lambda e_list_list: [''.join(e_list) for e_list in e_list_list]
    alias_entity = self.stat_data
    a2e = lambda e: alias_entity[e] if e in alias_entity else []
    sub_e_list = noEm(join_comb(comb(explode(ex))))
    sub_e_list += flat(list(map(a2e, sub_e_list)))
    sub_e_list = noEm(noEx(sub_e_list))
    print(sub_e_list)
    
    hopped_sub_e_list = noInvalidSubE([(sub_e, self.query(sub_e)) for sub_e in sub_e_list])
    all_hopped_ex_list = self.query(ex) + [(self.relations['sub_entity'], hopped_sub_e) for hopped_sub_e in hopped_sub_e_list]
    return (ex, all_hopped_ex_list)

  # return a json-like object
  # it defines a directed tree
  def buildMap(self, name):
    def _buildMap(name):
      data = self.getOneHop(name)
      for i in range(self.deep_level):
        expand = lambda t: (t[0] ,list(map(expand, t[1]))) if isinstance(t[1], list) else (t[0], expand(t[1])) if isinstance(t[1], tuple) else (t[0], (t[1], self._fullQuery(t[1])))
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

def test1():
  mb = MapBuilder()
  print(mb.getOneHop('薄熙来'))

def test2():
  mapBuilder = MapBuilder()
  mapBuilder.deep_level = 2
  q = mapBuilder.buildMap('薄熙来')
  print(q)

if __name__ == '__main__':
  test1()
