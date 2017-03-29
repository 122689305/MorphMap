#!/usr/bin/python
# coding:utf-8
import os
import sys

sys.path.insert(0,os.environ['MorphMap_HOME']+'/codes/myUtils')
from ThreadPool import ThreadPool, MyThread

from copy import deepcopy
import urllib
import re
import Queue

class WikiCrawler():
  regionRex = re.compile(r'(?s)<div id="content" class="mw-body" role="main">.*?</div>(?=\s*<div id="mw-navigation">)')
  linkRex = re.compile(r'<a[^>]*?href="(?P<href>[^"]*)"(?:(?!/>).)*?>\s*(?!<)(?P<entity_name>.*?)</a>')
  deepLevel = 3
  prefix = '/home/taoyuchao/MorphMap/output'

  def __init__(self):
    self.check_prefix()
    
  def check_prefix(self):
    if (not os.path.exists(self.prefix)) and (not os.path.isfile(self.prefix)):
      os.makedirs(self.prefix)

  def get_page(self, link):
    page = ""
    try:
      conn = urllib.urlopen(link)
      page = conn.read()
      print('page len: '+str(len(page)))
    except:
      print(sys.exc_info())
    return page

  def extract_links(self, cascadePage):
    cascadeLinkArray = []
    page = cascadePage.page
    pageRegionMatch = self.regionRex.search(page)
    if pageRegionMatch:
      pageRegion = pageRegionMatch.group()
    else:
      pageRegion = page
    linkMatchIter =self. linkRex.finditer(pageRegion)
    for linkMatch in linkMatchIter:
      linkMatchGroupDict = linkMatch.groupdict()
      link = linkMatchGroupDict['href']
      entityName = linkMatchGroupDict['entity_name']
      tmpCascadeLink = CascadeLink(link, cascadePage.cascadeEntityName)
      tmpCascadeLink.cascadeEntityName.names.append(entityName)
      cascadeLinkArray.append(tmpCascadeLink)
    return cascadeLinkArray

  def save_page(self, cascadePage):
    path = self.prefix
    for cascadeEntityName in cascadePage.cascadeEntityName[0:-1]:
      path += '/'+cascadeEntityName
      if not os.path.exists(path):
        os.mkdir(path)
    path = path + '/' + cascadePage.cascadeEntityName[-1] + '.html'
    if not os.path.exists(path):
      open(path, 'w').write(cascadePage.page)

  def isNeeded(self, cascadeLink):
    if len(cascadeLink.cascadeEntityName.names) > self.deepLevel:
      return False
    else:
      return True

  def run(self, cascadeLink):
    if self.isNeeded(cascadeLink):
      for name in cascadeLink.cascadeEntityName.names:
        print(name.decode('utf-8'))
      page = self.get_page(cascadeLink.link)
      cascadePage = CascadePage(page, cascadeLink.cascadeEntityName)
      self.save_page(cascadePage)
      return self.extract_links(cascadePage)

class CrawlerThread(MyThread):
  def run(self):
    while True:
      try:
        callable, args, kwargs = self.workQueue.get(timeout=self.timeout)
        res = callable(*args, **kwargs)
        for x in res:
          self.workQueue.put((callable, [x], {}))
      except Queue.Empty:
        break
      except :
        print(sys.exc_info())
        raise

class CrawlerThreadPool(ThreadPool):
  def __init__(self, *args, **kwargs):
    kwargs['Thread']=CrawlerThread
    super(CrawlerThreadPool, self).__init__(*args, **kwargs)

class CascadePage():
  def __init__(self, page, cascadeEntityName):
    self.page = page
    self.cascadeEntityName = deepcopy(cascadeEntityName)

class CascadeLink():
  def __init__(self, link, cascadeEntityName):
    self.link = link
    self.cascadeEntityName = deepcopy(cascadeEntityName)

class CascadeEntityName():
  def __init__(self, names):
    self.names = list(names)
  
  def __getitem__(self, index):
    return self.names[index]

  def __len__(self):
    return len(self.names)

def test():
  wikiCrawler = WikiCrawler()
  wikiCrawler.run(CascadeLink('https://zh.wikipedia.org/wiki/%E8%96%84%E7%86%99%E6%9D%A5',CascadeEntityName(['薄熙来'])))

if __name__ == '__main__':
  wikiCrawler = WikiCrawler()
  crawlerThreadPool = CrawlerThreadPool(14)
  crawlerThreadPool.add_job(wikiCrawler.run, CascadeLink('https://zh.wikipedia.org/wiki/%E8%96%84%E7%86%99%E6%9D%A5',CascadeEntityName(['薄熙来'])))
  crawlerThreadPool.wait_for_complete()
