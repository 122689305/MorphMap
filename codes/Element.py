# coding:utf-8

#import sys
#sys.path.insert(0, '../')
import os
from .Cache import cache, clearCache
import codes

cache_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'cache/element')

def enum(**enums):
  return type('Enum', (), enums)

class ElementList:
  cache_name = os.path.join(cache_dir, 'element_list')
  def __init__(self):
    self.element_list = cache(ElementList.cache_name, lambda :[])

  def __del__(self):
    print('__del__')
    clearCache(ElementList.cache_name)
    cache(ElementList.cache_name, lambda :self.element_list)

  def __getitem__(self, index):
    return self.element_list[index]
 
  def append(self, obj):
    self.element_list.append(obj) 
class Element:

  entity_dict = {}
  element_list = []

  def __init__(self, name='', children=[], parent=None, level=None, element_type=None, wv=None):
    self.name = name
    self.children = [] if children == [] else children
    self.parent = parent
    self.level = level
    self.element_type = element_type
    self.wv = wv

    if element_type == Element.ElementType.entity:
      if not name in Element.entity_dict:
        Element.entity_dict[name] = self
      else:
        self.children = Element.entity_dict[name].children
    
    Element.element_list.append(self)

  def _str_(self, prefix, e):
    s = ''
    prefix += ('--' if e.element_type == Element.ElementType.relation else '-->') + e.name + str(e.level)
    if e.children:
      for sub_e in e.children:
        if sub_e.parent == e:
          s += self._str_(prefix, sub_e)
    else:
      s = prefix+'\n'
    return s
    #return "{{'name':{0}, 'children':[{1}]}}".format(self.name, ','.join(map(lambda x:x._str_(), self.children)))

  def __str__(self):
    return self._str_('', self) 

  # get grand parent whose level is larger than it
  def getTrueParent(self):
    node = self.parent
    while node.parent and node.parent.level == node.level:
      node = node.parent
    return node

  @classmethod
  def concat(cls, element1, element2):
    element1.children.append(element2)
    element2.parent = element1
    element2.level = element1.level+1

  ElementType = enum(entity='entity', relation='relation')
