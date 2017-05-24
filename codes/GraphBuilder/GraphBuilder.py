# coding=utf-8
#import sys
#sys.path.append('../../')
import os
import pickle
import subprocess
import re
import json
from functools import partial
import sys
from codes import jieba
from codes.Element import Element
from codes.zhtools.langconv import *
from codes.GraphStatistics.AliasStatistics import AliasStatistics

'''
class Element:

  def __init__(self, name, children, parent=None, level=None, element_type=None, wv=None):

  ElementType = enum(entity='entity', relation='relation')
'''

class GraphBuilder:
  server_url = 'http://202.120.38.146:9600/data/sparql'
  cache_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../cache/entity')
  relations = {'sub_entity':'subEntity'}
#  stat_data = [(a_sts.count(), a_sts.ea2ae()) for a_sts in [AliasStatistics()]][0][1]
  stat_data = AliasStatistics().ea2ae()

  def __init__(self, root_entity_name):
    self.root = Element(name=root_entity_name, children=[], parent=None, level=0, element_type=Element.ElementType.entity)

  def __str__(self):
    return self.root.__str__()

  # Todo
  def getGraph(self):
    deep_level = 2
    def _getGraph():
      for i in range(deep_level):
        self.expandGraph(deep_level)
      return self.root
    self.root = self.cache(os.path.join(self.cache_dir, self.root.name), _getGraph) 
    return self.root

  def expandGraphFromOneElementWithMaxDeeplevel(self, e, deep_level):
    max_level = e.level + deep_level*2
    def _expand(e):
      if e.children == []:
        self.doElementOneHop(e)
      else:
        for sub_e in e.children:
          if sub_e.level < max_level and sub_e.level > e.level:
            _expand(sub_e)
    _expand(e)
    return e


  def expandGraphFromOneElement(self, e):
    def _expand(e):
      if e.children == []:
        self.doElementOneHop(e)
      else:
        for sub_e in e.children:
          if sub_e.level > e.level:
            _expand(sub_e)
    _expand(e)
    return e

  def expandGraph(self, deep_level = None):
    if deep_level:
      self.expandGraphFromOneElementWithMaxDeeplevel(self.root, deep_level)
    else:
      self.expandGraphFromOneElement(self.root)
    return self.root
    
  def encodeForQuery(self, name):
    name = name.replace(' ','_')
    return name

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
    name = self.encodeForQuery(name)
    (status, data) = self.rawQuery('http://zh.dbpedia.org/resource/'+name)
    if (status == 0):
      jo = json.loads(data)
      data = map(lambda yz: (yz['y']['value'].split('/')[-1], yz['z']['value'] if yz['z']['type'] != 'uri' else yz['z']['value'].split('/')[-1]), jo['results']['bindings'])
      data = list(data)
      return data
    else:
      return []

  # return [w1, w2, ...]
  # word segmentation. split in to queryful names
  def entitiesOf(self, literal):
    print(literal)
    literal =  Converter('zh-hans').convert(literal)
    flat = lambda L: sum(list(map(flat,L)),[]) if isinstance(L,list) else [L] 
    if literal:
      #sep = re.split(r"[：\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）!\"#$%&\'()*+,-./:;<=>?@\[\\\]\^_`{|}~\s]+",literal)
      #return flat(list(list(map(lambda x: list(jieba.cut(x)), sep)) + sep)) 

      sep = re.split(r"[：\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）!\"#$%&\'()*+,-./:;<=>?@\[\\\]\^_`{|}~\s]+",literal)
      e_list = list(map(lambda x: list(jieba.cut(x)), sep)) 

      #e_list = list(jieba.cut(literal))
# debug
#      e_list = re.split(r"\s+",literal)
# /debug
      e_list = list(filter(lambda e: e != '', e_list))
      return e_list
    else:
      return [literal]

  def doElementOneHop(self, element_ex):
    el_x = element_ex
    if not el_x.children:
      el_x.children = self.tup2graph(self.getOneHop(el_x.name), el_x.level, el_x).children

  def tup2graph(self, tup, init_level, init_el = None):
    def _tup2graph(tup, init_level, init_el = None):
      e_x, r_e_list = tup
      if init_el:
        el_x = init_el
      else:
        el_x = Element(name=e_x, level=init_level, element_type=Element.ElementType.entity) 
      for r,e in r_e_list:
        el_r = Element(name=r, element_type=Element.ElementType.relation)
        if isinstance(e, tuple):
          el_e = _tup2graph(e, init_level+2)
        else:
          el_e = Element(name=e, element_type=Element.ElementType.entity)
        Element.concat(el_x, el_r)
        Element.concat(el_r, el_e)
      return el_x
    return _tup2graph(tup, init_level, init_el)

  def getOneHop(self, ex):
    '''
    :parameter ex: entity x. just pass the name of this entity
    :return: (name, flat[ey, explode(ey), a2e(comb(explode(ey)))])
    '''
    from codes.GraphStatistics.AliasStatistics import AliasStatistics
    flat = lambda L: sum(list(map(flat,L)),[]) if isinstance(L,list) else [L]
  
    noEm = lambda e_list: list(filter(lambda e: e != '', e_list))
    noEx = lambda e_list: list(filter(lambda e: e != ex, e_list))
    noInvalidSubE = lambda hopped_e_list: list(filter(lambda hopped_e: len(hopped_e[1]) != 0 if isinstance(hopped_e, tuple) else True, hopped_e_list)) 
    explode = lambda e: self.entitiesOf(e)
    # redirects should be detected in GraphMatcher
    #comb = lambda e_list: [ [e_list[0]] + l for l in comb(e_list[1:])] + comb(e_list[1:]) if len(e_list) > 1 else [ [e_list[0]], [] ] if len(e_list) == 1 else [[]]
    comb = lambda e_list: [ e_list[i:j] for i in range(len(e_list)) for j in range(i+1,len(e_list)+1) ]
    join_comb = lambda e_list_list: [''.join(e_list) for e_list in e_list_list]
    alias_entity = self.stat_data
#    a2e = lambda e: alias_entity[e] if e in alias_entity else []
# debug
    a2e = lambda e: alias_entity[e][:5] if e in alias_entity else []
# /debug
    sub_e_list = noEm(flat([join_comb(comb(exploded_ex)) for exploded_ex in explode(ex)]))
    sub_e_list += flat(list(map(a2e, sub_e_list)))
    sub_e_list = noEm(noEx(sub_e_list))
    print(sub_e_list)
    
    hopped_sub_e_list = noInvalidSubE([(sub_e, self.query(sub_e)) if not sub_e in Element.entity_dict.keys() else sub_e for sub_e in sub_e_list])
    all_hopped_ex_list = self.query(ex) + [(self.relations['sub_entity'], hopped_sub_e) for hopped_sub_e in hopped_sub_e_list]
    data = (ex, all_hopped_ex_list)
    return data

  # cache
  def cache(self, filename, func, *args, **keywords):
    import os
    existed = os.path.isfile(filename)
    if existed:
      cached = open(filename, 'rb')
      return pickle.load(cached)
    else:
      data = func(*args, **keywords)
      pickle.dump(data, open(filename, 'wb'))
      return data

def test1():
  mb = GraphBuilder('薄熙来')
  mb.doElementOneHop(mb.root)
  print(mb)

def test2():
  mb = GraphBuilder('薄熙来')
  mb.expandGraph()
  mb.expandGraph()
  print(mb)

def test3():
  mb = GraphBuilder('薄熙来')
  print(mb.getGraph())

def test4():
  mb = GraphBuilder('李自成')
  print(mb.getGraph())

def test5():
  mb = GraphBuilder('薄熙来')
  mb.doElementOneHop(mb.root)
  for e in mb.root.children:
    if e.name == '姓名':
      print(e.children[0].children)
      mb.doElementOneHop(e.children[0])
  print(Element.entity_dict['薄熙来'].children)
  #print(mb)

def test6():
  mb = GraphBuilder('李自成')
  #mb.doElementOneHop(mb.root)
  mb.getGraph()
  print(mb)
  r = mb.root.children[1].children[0]
  e = r.children[0]
  print(id(r), r.name)
  print(id(e.parent), e.parent.name)

if __name__ == '__main__':
  test3()
  test4()
