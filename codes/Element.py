# coding:utf-8

import sys
sys.path.insert(0, '../')
import os
from codes.Cache import cache, clearCache

cache_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'cache/element')

def enum(**enums):
  return type('Enum', (), enums)

class EntityDict:
  cache_name = os.path.join(cache_dir, 'entity_dict')
  def __init__(self):
    self.entity_dict = cache(EntityDict.cache_name, lambda :{})

  def __del__(self):
    clearCache(EntityDict.cache_name)
    cache(EntityDict.cache_name, lambda :self.entity_dict)

class Element:

  entity_dict = EntityDict().entity_dict

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

  def _str_(self, prefix, e):
    s = ''
    prefix += ('--' if e.element_type == Element.ElementType.relation else '-->') + e.name + str(e.level)
    if e.children:
      for sub_e in e.children:
        if sub_e.level > e.level:
          s += self._str_(prefix, sub_e)
    else:
      s = prefix+'\n'
    return s
    #return "{{'name':{0}, 'children':[{1}]}}".format(self.name, ','.join(map(lambda x:x._str_(), self.children)))

  def __str__(self):
    return self._str_('', self) 

  @classmethod
  def concat(cls, element1, element2):
    element1.children.append(element2)
    element2.parent = element1
    element2.level = element1.level+1

  ElementType = enum(entity='entity', relation='relation')
