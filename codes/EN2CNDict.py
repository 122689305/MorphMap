import re
import os
class EN2CNDict:
  def __init__(self, dict_path=os.path.join(os.path.dirname(__file__), 'en2cn.dict')):
    f = open(dict_path, 'r')
    flat = lambda L: sum(list(map(flat,L)),[]) if isinstance(L,list) else [L]
    sp = lambda y: [s.strip() for s in re.split(r'[a-z]*?\.|,|\s+',re.sub(r'\[.*?\]|\(.*?\)|<.*?>', '', y)) if s]
    self.en2cn_dict = dict([(x, sp(y)) for l in f.readlines() for x,y in [tuple(re.split(r'\s+', l, maxsplit=1))]])

  def __getitem__(self, index):
    #print(index)
    data = self.en2cn_dict[index] if index in self.en2cn_dict else None
    return data

  def __iter__(self):
    return self.en2cn_dict.__iter__()
