# coding:utf-8
import re
import sys
import pickle
import time
class AliasStatistics():
  source_path = '../../../data/zhwiki-20161201-pages-articles-multistream.xml'
  cache_paths = {'entity_alias':'../cache/statistics/alias/entity_alias.pkl', 'alias_entity':'../cache/statistics/alias/alias_alias.pkl', 'entity_alias_meta':'../../output/statistics/alias/entity_alias_meta.pkl'}

  entity_link_re = re.compile(r'\[\[(.*?)\]\]')
  entity_alias_re = re.compile(r'^(?<!#)s?:?(.*?)(?:#.*(?=\|))?\|(.*)')
  filter_no_re = re.compile(r'(?:^s?:?(?:Category|Image|File)|^#).*')

  entity_alias_pair = {}  #{entity1: {alias1:count1, alias2:count2}, entity2}
  alias_entity_pair = {}  #{alias1: [entity1, entity2], alias2}

  def count(self):
    def _count():
      time_start = time.time()
      fi = open(self.source_path, 'r')
      ln = -1
      while True:
        ln += 1
        line = fi.readline()
# debug
        #if ln > 100000: break
        tl = 126417573
        per = ln*1.0/tl
        elap = time.time()-time_start
        remn = (1.0-per)*elap/per if per != 0 else 0
        prog = '[{0}{1}]'.format('*'*(int(per*100)), ' '*(100-int(per*100)))
        if ln%100000 == 0: sys.stdout.writelines('{5} {1}/{2} {0:.2f}%, {3:.2f}s elapesd, {4:.2f}s remained\r'.format(per*100, ln, tl, elap, remn, prog))
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
      return self.entity_alias_pair
    self.entity_alias_pair = self.cache(_count, self.cache_paths['entity_alias'])
    return self.entity_alias_pair

  def cache(self, func, filename):
    import os
    existed = os.path.isfile(filename)
    if existed:
      cached = open(filename, 'rb')
      return pickle.load(cached)
    else:
      data = func()
      pickle.dump(data, open(filename, 'wb'))
      return data

  def clearAllCache(self):
    for cache_path in self.cache_paths.values():
      self.clearCache(cache_path)
    
  def clearCache(self, filename): 
    import os
    existed = os.path.isfile(filename)
    if existed:
      os.remove(filename)    

  def metaCount(self):
    from numpy import sum, mean, std, array, size
    '''
    tot_entity
    tot_alias
    tot_alias_cnt
    ave_alias
    std_alias
    ave_alias_cnt
    std_alias_cnt
    ave_entity_ave_alias_cnt
    std_entity_ave_alias_cnt
    ave_entity_std_alias_cnt
    std_entity_std_alias_cnt
    '''
    time_start = time.time()
    # stat_data = [[1,3,2], [3,5], [1,2,1], ...]
    # stat_data = array(list(map(lambda entity__alias_dict:list(map(lambda alias_cnt: alias_cnt[1], entity__alias_dict[1].items())),  self.entity_alias_pair.items())))
    stat_data = map(lambda entity__alias_dict:list(map(lambda alias_cnt: alias_cnt[1], entity__alias_dict[1].items())),  self.entity_alias_pair.items())
    #alias_cnt_sum_data = array(list(map(lambda cnt_list: sum(cnt_list), stat_data)))
    #alias_cnt_size_data = array([len(cnt_list) for cnt_list in stat_data])
    #entity_ave_alias_cnt_data = array([mean(cnt_list) for cnt_list in stat_data])
    #entity_std_alias_cnt_data = array([std(cnt_list) for cnt_list in stat_data])
    flat = lambda L: sum(list(map(flat,L)),[]) if isinstance(L,list) else [L]

    #tot_entity = size(stat_data)
    #tot_alias = sum(alias_cnt_size_data)
    #tot_alias_cnt = sum(alias_cnt_sum_data)
    #ave_alias = mean(alias_cnt_size_data)
    #std_alias = std(alias_cnt_size_data)
    #ave_alias_cnt = mean(array(flat(stat_data)))
    #std_alias_cnt = std(flat(stat_data))
    #ave_entity_ave_alias_cnt = mean(entity_ave_alias_cnt_data)
    #std_entity_ave_alias_cnt = std(entity_ave_alias_cnt_data)
    #ave_entity_std_alias_cnt = mean(entity_std_alias_cnt_data)
    #std_entity_std_alias_cnt = std(entity_std_alias_cnt_data)

    tot_entity = 0
    tot_alias = 0
    tot_alias_cnt = 0
    ave_alias = 0
    std_alias = 0#
    ave_alias_cnt = 0
    std_alias_cnt = 0#
    ave_entity_ave_alias_cnt = 0#
    std_entity_ave_alias_cnt = 0#
    ave_entity_std_alias_cnt = 0#
    std_entity_std_alias_cnt = 0#

    for cnt_list in stat_data:
        tot_entity += 1
        tot_alias += len(cnt_list)
        tot_alias_cnt += sum(cnt_list)
    ave_alias = tot_alias*1.0 / tot_entity
    ave_alias_cnt = tot_alias_cnt*1.0 / tot_alias

    self.entity_alias_meta = {'tot_entity':tot_entity,'tot_alias':tot_alias,'tot_alias_cnt':tot_alias_cnt,'ave_alias':ave_alias,'std_alias':std_alias,'ave_alias_cnt':ave_alias_cnt,'std_alias_cnt':std_alias_cnt,'ave_entity_ave_alias_cnt':ave_entity_ave_alias_cnt,'std_entity_ave_alias_cnt':std_entity_ave_alias_cnt,'ave_entity_std_alias_cnt':ave_entity_std_alias_cnt,'std_entity_std_alias_cnt':std_entity_std_alias_cnt}
    return self.entity_alias_meta
    
def test1():
  alias_statistics = AliasStatistics()
  alias_statistics.clearAllCache()
  alias_statistics.count()

def test2():
  alias_statistics = AliasStatistics()
  alias_statistics.count()
  print(alias_statistics.entity_alias_pair)

def test3():
  alias_statistics = AliasStatistics()
  #print(alias_statistics.entity_alias_meta_path) 
  alias_statistics.count()
  #print('load entity_alias finished')
  alias_statistics.entity_alias_meta = alias_statistics.cache(alias_statistics.metaCount, alias_statistics.cache_paths['entity_alias_meta']) 
  for k,v in alias_statistics.entity_alias_meta.items():
    print('{0}:{1}'.format(k,v))

if __name__ == '__main__':
  test3() 
