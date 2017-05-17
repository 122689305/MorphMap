# coding:utf-8

def enum(**enums):
  return type('Enum', (), enums)

class Element:

  def __init__(self, name, children, parent=None, level=None, element_type=None, wv=None):
    self.name = name
    self.children = children
    self.parent = parent
    self.level = level
    self.element_type = element_type
    self.wv = wv
    def __str__(self):
      return "{{'name':{0}, 'parent':{1}, 'children':[{2}]}}".format(self.name, self.parent, ','.join(map(lambda x:x.__str__(), self.children)))

  ElementType = enum(entity='entity', relation='relation')

