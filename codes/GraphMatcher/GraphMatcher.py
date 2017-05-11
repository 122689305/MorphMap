# coding:utf-8
import sys
sys.path.append('../../')
from codes.MapBuilder.MapBuilder import MapBuilder
from functools import partial

def enum(**enums):
  return type('Enum', (), enums)

class GraphMatcher:
  class Element:
    def __init__(self, name, children, parent=None, level=None, nodetype=None):
      self.name = name
      self.children = children
      self.parent = parent
      self.level = level
      self.nodetype = nodetype
    def __str__(self):
      return "{{'name':{0}, 'parent':{1}, 'children':{2}}}".format(self.name, self.parent, ''.join(map(lambda x:x.__str__(), self.children)) if isinstance(self.children, list) else '')
    Nodetype = enum(entity='entity', relation='relation')

  def __init__(self):
    # each pair represents a match
    self.element_pair = {}

  def isSimilar(self, element1, element2):
    # please update this accordding to the structure of the Element
    return element1.name == element2.name

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
    setLevelAndNodeType(graph)
    return graph

  def updatePairTable(self, element1, element2):
    if element1 in self.element_pair:
      self.element_pair[element1].append(element2)
    else:
      self.element_pair[element1] = [element2]

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

def testSearch(g):
  lg = gm.deepSearch(g)
  for node in list(lg):
    print(node.name, node.level, node.nodetype, node.parent.name if node.parent else '')
  lg = gm.wideSearch(g)
#  for node in list(lg):

def testFind(gm, g1, g2):
  gm.findElementPairs(g1,g2)
  print(len(gm.element_pair))

if __name__ == '__main__':
  gm = GraphMatcher()
  mb = MapBuilder()
  mb.deep_level = 1 
  t1 = mb.buildMap('薄熙来')
  g1 = gm.tuple2Graph(t1)
  t2 = mb.buildMap('李自成')
  g2 = gm.tuple2Graph(t2)
  #testSearh(g)
  testFind(gm, g1, g2)
