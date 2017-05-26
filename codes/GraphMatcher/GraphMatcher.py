# coding:utf-8
import sys
sys.path.append('../../')
#from codes.MapBuilder.MapBuilder import MapBuilder
from codes.GraphBuilder.GraphBuilder import GraphBuilder
from codes.Element import Element
from codes.Cache import cache
from codes.util import showComputingTime
from codes.EN2CNDict import EN2CNDict
from functools import partial
import pickle
import gensim
from codes import jieba
import re
import os
import urllib 
import math
import itertools
  
class GraphMatcher:

  w2v_model_dir = '/home/bill/cdminer/ijcai/corpus_data/w2v/chineseembedding_0207_toload.txt'
  wv_sim_thre = 0.7
  w2v_web_url = 'http://202.120.38.146:9602'

  def __init__(self):
    # each pair represents a match
    self.element_pair = {}
    self.chain_pair = {}
    #self.model_cn = gensim.models.Word2Vec.load_word2vec_format(self.w2v_model_dir,binary=False)
    #self.model_cn = gensim.models.KeyedVectors.load_word2vec_format(self.w2v_model_dir, binary=False)
    self.en2cn_dict = EN2CNDict(os.path.join(os.path.dirname(__file__), '../en2cn.dict'))
    self.cache_dir = os.path.join(os.path.dirname(__file__), '../cache/matcher')

  # return a list of comparable words. Like 'king' -> ['king', '国王', '君主']
  # all words in the list will be compared by word vector
  def getComparableList(self, literal):
    flat = lambda L: sum(list(map(flat,L)),[]) if isinstance(L,list) else [L]
    cbl = set([literal])
    sep = [x.lower() for x in re.split(r"[：\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）!\"#$%&\'()*+,-./:;<=>?@\[\\\]\^_`{|}~\s]+|([A-Z][a-z]*)", literal) if x]
    cbl |= set(sep)
    sep = flat([self.en2cn_dict[x] for x in sep if x in self.en2cn_dict])
    cbl |= set(sep)
    #sep = flat([list(jieba.cut(x)) for x in sep])
    #cbl |= set(sep)
    return list(cbl)

  def getW2VSimilarity(self, name1, name2):
    #for x in [name1, name2]:
    #  x = x.encode('utf-8')
    data = urllib.parse.urlencode({'w1':name1, 'w2':name2})
    url = 'http://202.120.38.146:9602/?{0}'.format(data)
    f = urllib.request.urlopen(url)
    if f.getcode() == 200:
      return eval(f.readline())
    else:
      return None;

  def getScore(self, element1, element2):
    sc = -1
    if element1.name == element2.name:
      sc = 1
    else:
      try:
        sc = max(filter(lambda x:x, [self.getW2VSimilarity(n1, n2) for n1 in self.getComparableList(name1) for n2 in self.getComparableList(name2)]))
      except:
        sc = -1
    e = lambda x:math.pow(math.e, x)
    f = lambda x:-1 + 2*((e(x)-e(-1))/(e(1)-e(-1)))
    sc = f(sc)
    return sc  

  def getSameLevel(self, node):
    flat = lambda L: sum(list(map(flat,L)),[]) if isinstance(L,list) else [L]
    def _getSameLevel(node, level):
      if node.level == level and (not node.name == 'subEntity' or len(node.children[0].children)<20): # add small subEntity feature
        return [node] + flat([_getSameLevel(x, level) for x in node.children if x.parent == node])
      else:
        return []
    if node.element_type == Element.ElementType.relation:
      return [node]
    else:
      data = _getSameLevel(node, node.level)
      return list(filter(lambda x:x.element_type==Element.ElementType.entity, data))

  def layerSearch(self, node):
    flat = lambda L: sum(list(map(flat,L)),[]) if isinstance(L,list) else [L]
    node_list = [node]
    while node_list:
      node_list = flat([self.getSameLevel(x) for x in node_list])
      yield node_list
      node_list = [x for _x in node_list for x in _x.children if x.parent == _x and x.level > _x.level] # control loop and subEntity, wikiPageRedirects

  def cachedComputeBiGraphScore(self, graph1, graph2):
    filename = os.path.join(self.cache_dir, graph1.root.name +'_'+graph2.root.name)
    return cache(filename, self.computeBiGraphScore, graph1, graph2)

  @showComputingTime
  def computeBiGraphScore(self, graph1, graph2):
    alpha = 0.8 # the parameter to control the distance panishment
    graph_list = [graph1.root, graph2.root]
    gen_node_list = [self.layerSearch(g) for g in graph_list]
    node_pair_score_dict = {(None, None):0}
    for node_list_list, n in zip(zip(*gen_node_list), itertools.count(0)):
      print('layer {0}'.format(n))
      #for node_list in node_list_list:
      #  print()
      #  for node in node_list:
      #    print(node.name, type(node.getTrueParent()))
      gen_node_pair = itertools.product(*node_list_list)  
      for node_pair in gen_node_pair:
        score = self.getScore(*node_pair)
        parent_pair = tuple([x.getTrueParent() for x in node_pair])
        if not parent_pair in node_pair_score_dict: 
          for pair in parent_pair: print(pair.getHistoryText())
        score += node_pair_score_dict[parent_pair]*alpha 
        node_pair_score_dict[node_pair] = score
    del node_pair_score_dict[(None, None)]
    score_list = self.sortedNodePairScoreDict(node_pair_score_dict)
    score_list = list(filter(lambda kv:kv[0][0].element_type != Element.ElementType.relation, score_list))
    #print(score_list)
    return score_list

  @showComputingTime
  def sortedNodePairScoreDict(self, node_pair_score_dict):
    return sorted(node_pair_score_dict.items(), key=lambda d:d[1], reverse=True)

  def isSimilar(self, element1, element2):
    # please update this accordding to the structure of the Element
    #return element1.name == element2.name
      def roundSimilar(element1, element2):
        pool = []
        for i in ['', '@@@']:
          for j in ['', '@@@']:
            name1 = element1.name + i
            name2 = element2.name + j
            try:
              pool.append(model_cn.wv.similarity(element1.name, element2.name))
            except Exception:
              pass
        return pool
      pool = roundSimilar(element1, element2)
      if pool:
        return max(pool) > self.wv_sim_thre
      else:
        return element1.name == element2.name

  def getWordVector(self, name):
    try:
      return self.model_cn.wv[name]
    except Exception:
      return None

  def tuple2Graph(self, tuple_map):
    #f = lambda x_L, p:(Element(x_L[0], x_L[1], p), map(partial(f, p=x_L[0]), x_L[1]) if isinstance(x_L[1], list) else Element(x_L[1])) 
    # changed to list
    f = lambda L: Element(L[0], list(map(f, L[1])) if isinstance(L[1], list) else [f(L[1])] if isinstance(L[1], tuple) else [Element(L[1], [])] )  
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
        node.element_type = Element.ElementType.entity if level % 2 == 0 else Element.ElementType.relation
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
    self.chain_pair = self.cacheChainPairs(graph1, graph2, _findChainPairs)
    return self.chain_pair

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
        while node:
          name = '\v' + node.name if h == height else node.name
          line = ' --' + name + line if node.element_type == Element.ElementType.relation else '--> ' + name + line
          node = node.parent
          h += 1
        print(line)
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
    print(node.name, node.level, node.element_type, node.parent.name if node.parent else '')
  lg = gm.wideSearch(g)
#  for node in list(lg):

def testFindEle(gm, g1, g2):
  gm.findElementPairs(g1,g2)
  print(len(gm.element_pair))

def testFindChain(gm, g1, g2):
  gm.findChainPairs(g1, g2)
  print(len(gm.chain_pair))
  gm.sortedChainPairs()
  gm.printSortedChainPairs(1000)
  #print(std[0] if std else '')

def test1():
  gm = GraphMatcher()
  mb = MapBuilder()
  mb.deep_level = 2 
  t1 = mb.buildMap('薄熙来')
  g1 = gm.tuple2Graph(t1)
  t2 = mb.buildMap('李自成')
  g2 = gm.tuple2Graph(t2)
  #testSearh(g)
  #testFindEle(gm, g1, g2)
  testFindChain(gm ,g1, g2)

def test2():
  gm = GraphMatcher()
  gb1 = GraphBuilder('薄熙来').getGraph()
  gb2 = GraphBuilder('李自成').getGraph()
  testFindChain(gm, gb1, gb2)

def test3():
  di = EN2CNDict(os.path.join(os.path.dirname(__file__), '../en2cn.dict'))
  print(di.en2cn_dict['king'])

def test4():
  gm = GraphMatcher()
  l = gm.getComparableList('termStart')
  print(l)

def test5():
  gm = GraphMatcher()
  for x,y in [('主席', '首领'), ('前进', '行进'), ('杀戮','刺杀'),  ('皇帝', '皇上'), ('晴天', '晴朗'), ('傻瓜', '笨蛋'), ('学习','进修'), ('得意', '骄傲'), ('环境', '杯子'), ('丑八怪', '小吃'), ('无所谓', '抽纸'), ('书本', '吃饭'), ('强制', '哈气'), ('宝贝', '革命'), ('睡觉', '宇宙飞船'), ('宜家','字符'), ('宜家', '挑战')]:
    sc = gm.getW2VSimilarity(x,y)
    grid = 60
    pro = int((sc+1)/2.0*grid)
    if pro > grid//2:
      pro = ' '*(grid//2-1) + '^' + '+'*(pro-grid//2-1) + '*' + ' '*(grid-pro)
    elif pro == grid//2:
      pro = ' '*(grid//2-1) + '*'
    else:
      pro = ' '*(pro-1) + '*' + '-'*(grid//2 - pro-1) + '^' + ' '*(grid//2)
    print('{3} |{0} and {1}: {2}'.format(x,y,sc,pro))

def test6():
  gm = GraphMatcher()
  gb = GraphBuilder('太祖')
  gb.getGraph()
  layer = gm.layerSearch(gb.root)
  cnt = 0
  for l in layer:
    print('{1}layer:{0}{1}'.format(cnt, '-'*20))
    for x in l:
      print(x.name, end=' ')
    print()
    print()
    cnt += 1
    #if cnt > 3:
      #break
  print(cnt)

def test7():
  gm = GraphMatcher()
  gb1 = GraphBuilder('平西王')
  gb2 = GraphBuilder('薄熙来')
  gb1.getGraph()
  gb2.getGraph()
  score_list = gm.cachedComputeBiGraphScore(gb1, gb2)
  #score_dict = gm.cachedComputeBiGraphScore(gb1, gb2)
  #score_list = gm.sortedNodePairScoreDict(score_dict)
  cnt = 0
  for k,v in score_list:
    n1,n2 = k
    cnt += 1
    if cnt < 0: continue
    if all([n1,n2]):
      print(n1.name, n2.name, v)
      print(n1.getHistoryText())
      print(n2.getHistoryText())
    if cnt > 100: break

def test8():
  gm = GraphMatcher()
  entity_morph=[('薄熙来', '平西王'), ('毛泽东', '太祖'), ('陈光诚', '盲人'), ('王立军','西南王警官'),('德文·韦德', '闪电侠'), ('金正恩', '金胖子'), ('蒋介石', '常公公'), ('杨幂','函数')]
  for em in entity_morph:
    print('{0}{1}{0}'.format('-'*20, em))
    score_list = gm.cachedComputeBiGraphScore(*[GraphBuilder(x).getGraph() for x in em])
    for score, n in zip(score_list, range(100)):
      (n1, n2), v = score
      print(n, n1.name, n2.name, v)
      print(n1.getHistoryText()) 
      print(n2.getHistoryText())

def test9():
  gm = GraphMatcher()
  entity_morph=[('薄熙来', '平西王'), ('毛泽东', '太祖'), ('陈光诚', '盲人'), ('王立军','西南王警官'),('德文·韦德', '闪电侠'), ('金正恩', '金胖子'), ('蒋介石', '常公公'), ('杨幂','函数')]
  index = 1
  for em in [entity_morph[index]]:
    graph_list = [GraphBuilder(x).getGraph() for x in em]
    #[print(graph) for graph in graph_list]
    score_list = gm.cachedComputeBiGraphScore(*graph_list)
    for score, n in zip(score_list, range(100)):
      (n1, n2), v = score
      print(n, n1.name, n2.name, v)
      print(n1.getHistoryText())
      print(n2.getHistoryText())



if __name__ == '__main__':
  test8()
