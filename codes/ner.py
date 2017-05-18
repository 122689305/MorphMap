#coding:utf-8
import urllib
import urllib2
import httplib
import re
import json
import subprocess
import datetime

headers = {'Content-Type' :'text/plain; charset=UTF-8', 'Connection':'keep-alive'}

prop = \
{'properties':re.sub(r'\s','','''{
"annotators" : "tokenize,ssplit,pos,ner",
"outputFormat" : "json",

"tokenize.language" : "zh",
"segment.model" : "edu/stanford/nlp/models/segmenter/chinese/ctb.gz",
"segment.sighanCorporaDict" : "edu/stanford/nlp/models/segmenter/chinese",
"segment.serDictionary" : "edu/stanford/nlp/models/segmenter/chinese/dict-chris6.ser.gz",
"segment.sighanPostProcessing" : "true",

"ssplit.boundaryTokenRegex" : "[.]|[!?]+|[。]|[！？]+",

"pos.model" : "edu/stanford/nlp/models/pos-tagger/chinese-distsim/chinese-distsim.tagger",

"ner.model" : "edu/stanford/nlp/models/ner/chinese.misc.distsim.crf.ser.gz",
"ner.applyNumericClassifiers" : "false",
"ner.useSUTime" : "false",

"parse.model" : "edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz",

"depparse.model   " : "edu/stanford/nlp/models/parser/nndep/CTB_CoNLL_params.txt.gz",
"depparse.language" : "chinese",

"coref.sieves" : "ChineseHeadMatch, ExactStringMatch, PreciseConstructs, StrictHeadMatch1, StrictHeadMatch2, StrictHeadMatch3, StrictHeadMatch4, PronounMatch",
"coref.input.type" : "raw",
"coref.postprocessing" : "true",
"coref.calculateFeatureImportance" : "false",
"coref.useConstituencyTree" : "true",
"coref.useSemantics" : "false",
"coref.mode" : "hybrid",
"coref.algorithm" : "hybrid",
"coref.path.word2vec" : "",
"coref.language" : "zh",
"coref.defaultPronounAgreement" : "true",
"coref.zh.dict" : "edu/stanford/nlp/models/dcoref/zh-attributes.txt.gz",
"mention.print.log" : "false",
"mention.type" : "RULE"
}''')
}

def json_detector_shell(content):
  cmd = '''awk -F{ '{for(i=1;i<=NF;i++)print $i}' | sed -n '/ner/p' | sed '/"ner":"O"/s/.*//'| sed 's/.*"word":"\(.*\)","originalText.*"ner":"\(.*\)"},/\\1|\\2|/;' | awk BEGIN{RS=EOF}'{gsub(/\\n/," ");print}' | sed ':a;s/ //;t a' |awk -F '|' '{printf("%s ",$2);for(i=1;i<NF;i+=2)printf("%s",$i);printf("\\n");}' '''
  p = subprocess.Popen(cmd, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
  p.stdin.write(content)
  p.stdin.close()
  entity = p.stdout.read()
  return entity

def json_detector_py(content):
  cnt = 0
  previous_ner = ''
  entity = ''
  json_blocks = content.split('{')
  entity_content = ''
  for line in json_blocks:
    re_word_ner = re.search(r'"word":"(.*?)".*?"ner":"(.*?)"', line)
    cnt += 1
    if re_word_ner:
      word = re_word_ner.group(1)
      ner = re_word_ner.group(2)
      if not ner == 'O':
        if ner == previous_ner:
          entity += word
        else:
          if not previous_ner == 'O':
            entity_content += previous_ner+' '+entity+'\n'
            print previous_ner, entity
          else:
            entity = word
      else:
        if not entity == '':
          entity_content += previous_ner+' '+entity+'\n'
          print previous_ner, entity
          entity = ''
      previous_ner = ner
  return entity_content

# print prop
url = '/?'+urllib.urlencode(prop)
conn = httplib.HTTPConnection("localhost",9000)
# print url

begin = datetime.datetime.now()

data = {'text':'双十一是指每年11月11日（光棍节）的网络促销日。今天人特别多，尤其是旧金山。'}
for f_name in ['../../data/long_abstracts_zh.ttl']:
#for f_name in ['../../data/zhwiki-20161201-pages-articles-multistream.xml']:
# for f_name in ['../week20_text.txt', '../week31_text.txt', '../week40_text.txt']:
#for f_name in ['../week10_text.txt', '../week20_text.txt', '../week31_text.txt', '../week40_text.txt']:
# for f_name in ['../week1_text.txt', '../week10_text.txt', '../week20_text.txt', '../week31_text.txt', '../week40_text.txt']:
# for f_name in ['../week1_text.txt']:
  f = open(f_name)
  #f_o = open(f_name.replace('text','entity'),'w')
  f_o = open('../output/named_entity_list', 'w')
  # data = {'text':f.readline()+'\n'+f.readline()}
  # print data
  cnt = 1
  while True:
    l = ''
    for i in xrange(10):
      l += f.readline()
      l += '\n'
      cnt += 1
    print 'read finished'
    # if cnt < 44: continue
    # if cnt > 44: break
    # if cnt >= 1002: break
    #if cnt >= 700000: break 
    if not l: break
    data_urlencode = urllib.quote_plus(l)
    print 'data coded'
    conn.request(url=url, method="POST", headers=headers, body=data_urlencode)
    print 'request finished'
    res = conn.getresponse()
    content = res.read()
    # print res.getheaders()
    # print content
    # open('ner3.json','w').write(content)
    print cnt-1, res.status, res.reason
    if res.status != 200 : continue 
    # entity = json_detecor_shell(content)
    entity = json_detector_py(content)
    # entity = json_detector_shell(content)
    if len(entity) != 0:
      print entity[:50]
      f_o.write(entity)
    # print content
    # open('ner.json','w').write(content)
    # break
  f_o.close()

end = datetime.datetime.now()
print end-begin


# p_cat = subprocess.Popen('cat ner.json', stdout = subprocess.PIPE, shell=True)

