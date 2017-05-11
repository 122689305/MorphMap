# coding:utf-8
import sys
sys.path.append('../../')
from codes.MapBuilder.MapBuilder import MapBuilder
from functools import partial
import pickle
import gensim

def enum(**enums):
  return type('Enum', (), enums)

class GraphMatcher:

  w2v_model_dir = '/home/bill/cdminer/ijcai/corpus_data/w2v/chineseembedding_0207_toload.txt'
  cache_dir = '../cache'
  wv_sim_thre = 0.7

  class Element:
    def __init__(self, name, children, parent=None, level=None, nodetype=None, wv=None):
      self.name = name
      self.children = children
      self.parent = parent
      self.level = level
      self.nodetype = nodetype
      self.wv = wv
#    def __str__(self):
#      return "{{'name':{0}, 'parent':{1}, 'children':{2}}}".format(self.name, self.parent, ''.join(map(lambda x:x.__str__(), self.children)) if isinstance(self.children, list) else '')
    Nodetype = enum(entity='entity', relation='relation')

  def __init__(self):
    # each pair represents a match
    self.element_pair = {}
    self.chain_pair = {}
    #self.model_cn = gensim.models.Word2Vec.load_word2vec_format(self.w2v_model_dir,binary=False)

  def isSimilar(self, element1, element2):
    # please update this accordding to the structure of the Element
    #return element1.name == element2.name
    try:
      return model_cn.wv.similarity(element1.name, element2.name) > self.wv_sim_thre
    except Exception:
      return element1.name == element2.name

  def getWordVector(self, name):
    try:
      return self.model_cn.wv[name]
    except Exception:
      return None

  def tuple2Graph(self, tuple_map):
    #f = lambda x_L, p:(self.Element(x_L[0], x_L[1], p), map(partial(f, p=x_L[0]), x_L[1]) if isinstance(x_L[1], list) else self.Element(x_L[1])) 
    # changed to list
    f = lambda L: self.Element(L[0], list(map(f, L[1])) if isinstance(L[1], list) else [f(L[1])] if isinstance(L[1], tuple) else [self.Element(L[1], [])] )  
    graph = f(tuple_map)
    def setParent(root):
      def _setParent(node, parent):
        node.parent = parent
        if node.children:
          for _node in node.children:
            _setParent(_node, node)
      _setParent(root, None)
    setParent(graph)
    def setLevelAndNodeType(root):
      def _setLevelAndNodeType(node, level):
        node.level = level
        node.nodetype = self.Element.Nodetype.entity if level % 2 == 0 else self.Element.Nodetype.relation
        if node.children:
          for _node in node.children:
            _setLevelAndNodeType(_node, level+1)
      _setLevelAndNodeType(root, 0)
    #def setWordVector(root):
    #  def _setWordVector(root):
            
    setLevelAndNodeType(graph)
    return graph

  def updatePairTable(self, element1, element2):
    if element1 in self.element_pair:
      self.element_pair[element1].append(element2)
    else:
      self.element_pair[element1] = [element2]

  def updateChainTable(self, element1, element2, height):
    if element1 in self.chain_pair:
      self.chain_pair[element1].append((element2, height))
    else:
      self.chain_pair[element1] = [(element2, height)]

  def deepSearch(self, graph_node):
    yield graph_node
    if graph_node.children:
      for node in graph_node.children:
        for _node in self.deepSearch(node):
          yield _node

  def wideSearch(self, graph_node):
    def _wideSearch(node_list):
      if node_list:
        for node in node_list:
          yield node
        for _node in _wideSearch(sum([node.children for node in node_list], [])):
          yield _node
    return _wideSearch([graph_node])

  def findElementPairs(self, graph1, graph2):
    self.element_pair = {}
    gi1 = self.deepSearch(graph1)
    for node1 in gi1:
      gi2 = self.deepSearch(graph2)
      for node2 in gi2:
        if (self.isSimilar(node1, node2)):
          self.updatePairTable(node1, node2)
    return self.element_pair

  def findChainPairs(self, graph1, graph2):
    def _findChainPairs(graph1, graph2):
      self.chain_pair = {}
      self.findElementPairs(graph1, graph2)
      for element1, element2_list in self.element_pair.items():
        for element2 in element2_list:
          f = lambda node1, node2, height: f(node1.parent, node2.parent, height+1) if self.isSimilar(node1.parent, node2.parent) else height
          self.updateChainTable(element1, element2, f(element1, element2, 0))
      return self.chain_pair
    return self.cacheChainPairs(graph1, graph2, _findChainPairs)

  def sortedChainPairs(self):
    flat = lambda L: sum(list(map(flat,L)),[]) if isinstance(L,list) else [L]
    list_chain_pair = list(map(lambda tup: [(tup[0], _tup[0], _tup[1]) for _tup in tup[1]], self.chain_pair.items()))
    list_chain_pair = flat(list_chain_pair)
    list_chain_pair = sorted(list_chain_pair, key=lambda e1_e2_h: e1_e2_h[2], reverse=True)
    self.list_chain_pair = list_chain_pair

  def printSortedChainPairs(self, top=10):
    _top = 0
    for chain_pair in self.list_chain_pair:
      if (_top == top): break
      _top += 1
      (element1, element2, height) = chain_pair
      for element in [element1, element2]:
        node = element
        line = ''
        h = 0
        tail_len = 0
        while node:
          name = node.name 
          line = ' --' + name + line if node.nodetype == self.Element.Nodetype.relation else '--> ' + name + line
          if h == height: tail_len = len(line)
          node = node.parent
          h += 1
        twoline = line[:-tail_len] + '\n' + ' '*len(line[:-tail_len]) + line[-tail_len:]
        print(twoline)
      print()
           

  def cacheChainPairs(self, graph1, graph2, func):
    import os
    name = graph1.name + '_' + graph2.name + '_pair'
    filename = os.path.join(self.cache_dir, name)
    existed = os.path.isfile(filename)
    if existed:
      cached = open(filename, 'rb')
      return pickle.load(cached)
    else:
      data = func(graph1, graph2)
      pickle.dump(data, open(filename, 'wb'))
      return data


def testSearch(g):
  lg = gm.deepSearch(g)
  for node in list(lg):
    print(node.name, node.level, node.nodetype, node.parent.name if node.parent else '')
  lg = gm.wideSearch(g)
#  for node in list(lg):

def testFindEle(gm, g1, g2):
  gm.findElementPairs(g1,g2)
  print(len(gm.element_pair))

def testFindChain(gm, g1, g2):
  gm.findChainPairs(g1, g2)
  print(len(gm.chain_pair))
  gm.sortedChainPairs()
  gm.printSortedChainPairs()
  #print(std[0] if std else '')


if __name__ == '__main__':
  gm = GraphMatcher()
  mb = MapBuilder()
  mb.deep_level = 1
  t1 = mb.buildMap('薄熙来')
  g1 = gm.tuple2Graph(t1)
  t2 = mb.buildMap('李自成')
  g2 = gm.tuple2Graph(t2)
  #testSearh(g)
  #testFindEle(gm, g1, g2)
  testFindChain(gm ,g1, g2)
