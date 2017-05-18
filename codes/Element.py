# coding:utf-8

def enum(**enums):
  return type('Enum', (), enums)

class Element:

  def __init__(self, name='', children=[], parent=None, level=None, element_type=None, wv=None):
    self.name = name
    self.children = [] if children == [] else children
    self.parent = parent
    self.level = level
    self.element_type = element_type
    self.wv = wv

  def _str_(self, prefix, e):
    s = ''
    prefix += ('--' if e.element_type == Element.ElementType.relation else '-->') + e.name
    if e.children:
      for sub_e in e.children:
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

