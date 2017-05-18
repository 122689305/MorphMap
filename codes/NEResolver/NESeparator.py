# coding:utf-8
import os
ne_dir = '../../output/named_entity'
ne_list_path = '../../output/tmp_named_entity_list'
'''
GPE 釜山
ORG 基督教神學院
GPE 釜山
GPE 釜山
MISC 忠清南道天安
PERSON 大衛·當臣
'''

def separate():
  ne_type_list = ['GPE', 'ORG', 'MISC', 'PERSON', 'LOC']
  ne_files = eval('{{{0}}}'.format(','.join(["'{0}': open(os.path.join(ne_dir, '{0}'), 'w')".format(t) for t in ne_type_list])))
  
  ne_list_f = open(ne_list_path, 'r')
  while True:
    line = ne_list_f.readline()
    if not line:
      break
    line = line.strip()
    sep_p = line.find(' ')
    ne_type = line[:sep_p]
    entity = line[sep_p+1:]
    ne_files[ne_type].write(entity+'\n')

if __name__ == '__main__':
  separate()
