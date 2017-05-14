# coding:utf-8
import re
import sys
import pickle
class AliasStatistics():
  source_path = '../../../data/zhwiki-20161201-pages-articles-multistream.xml'
  cache_path = '../../output/statistics/alias/alias.pkl'

  entity_link_re = re.compile(r'\[\[(.*?)\]\]')
  entity_alias_re = re.compile(r'^(?<!#)s?:?(.*?)(?:#.*(?=\|))?\|(.*)')
  filter_no_re = re.compile(r'(?:^s?:?(?:Category|Image|File)|^#).*')

  entity_alias_pair = {}  #{entity1: {alias1:count1, alias2:count2}, entity2}
  alias_entity_pair = {}  #{alias1: [entity1, entity2], alias2}

  def count(self):
    fi = open(self.source_path, 'r')
    fo = open(self.cache_path, 'wb')
    ln = -1
    while True:
      ln += 1
      line = fi.readline()
# debug
      if ln > 100000: break
# /debug
      if not line: break
      for entity_link in self.entity_link_re.findall(line):
# debug
        #print(entity_link)
# /debug
        alias_match = self.entity_alias_re.match(entity_link)
        if alias_match:
          if self.filter_no_re.match(entity_link):
# debug
            #sys.stderr.write('filter out (line: {0}): {1}\n'.format(ln, entity_link))
# /debug
            break
# debug
          #print('entity (line: {0}): {1}'.format(ln, entity_link))
# /debug
          entity = alias_match.group(1)
          alias = alias_match.group(2)
# debug
          #print('entity: {0}, alias: {1}'.format(entity, alias))
# /debug
# debug
                    
          if re.match('\s+', alias):
            sys.stderr.write('empty alias (line:{1}): {0}\n'.format(alias, ln))
          if self.entity_alias_re.match(entity) or self.entity_alias_re.match(alias):
            sys.stderr.write('multi \'|\' (line: {0}): {1}\n'.format(ln, entity_link))
          
# /debug
          if entity in self.entity_alias_pair:
            if alias in self.entity_alias_pair[entity]:
              self.entity_alias_pair[entity][alias] += 1
            else:
              self.entity_alias_pair[entity][alias] = 1 
          else:
            self.entity_alias_pair[entity] = {alias:1}
# debug
    #print(self.entity_alias_pair)
# /debug
    pickle.dump(self.entity_alias_pair, fo, 2)
'''
  def cache(self, func):
    import os
    if os.    
'''
if __name__ == '__main__':
  alias_statistics = AliasStatistics()
  alias_statistics.count()
