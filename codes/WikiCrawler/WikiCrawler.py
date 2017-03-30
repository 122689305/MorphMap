#!/usr/bin/python
# coding:utf-8
from __future__ import print_function
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
  linkRex = re.compile(r'<a[^>]*?href="(?P<href>[^"]*)"(?:(?!/>)[^>])*?>\s*(?!<)(?P<entity_name>.*?)</a>')
  rootLinkRex = re.compile(r'(?P<rootLink>.*?://[^/]*)')
  subLinkRex = re.compile(r'^/(?!/).*')
  tagLinkRex = re.compile(r'^#.*')
  filenameFilter = lambda self, x: re.sub(r'/', '-', x)
  deepLevel = 3
  prefix = os.environ['MorphMap_HOME']+'/output'

  def __init__(self):
    self.check_prefix()
    
  def check_prefix(self):
    if (not os.path.exists(self.prefix)) and (not os.path.isfile(self.prefix)):
      os.makedirs(self.prefix)

  def get_page(self, link):
    if not link:
      return None
    page = None
    try:
      print(link)
      conn = urllib.urlopen(link)
      page = conn.read()
      print('page len: '+str(len(page)))
    except:
      print('get_page')
      print(sys.exc_info())
    return page

  def get_root_link(self, parentLink):
    rootLinkMatch = self.rootLinkRex.search(parentLink)
    if rootLinkMatch:
      rootLinkMatchGroupDict = rootLinkMatch.groupdict()
      rootLink = rootLinkMatchGroupDict['rootLink']
    else:
      rootLink = parentLink
    return rootLink

  def get_full_link(self, link, parentLink):
    if self.subLinkRex.match(link): # relative link
      return self.get_root_link(parentLink)+'/'+link
    elif self.tagLinkRex.match(link): # link started with '#'. tag link
      return None
    else: # normal link
      return link

  def extract_links(self, cascadePage):
    if not cascadePage.page:
      return []
    cascadeLinkArray = []
    page = cascadePage.page
    pageRegionMatch = self.regionRex.search(page)
    if pageRegionMatch:
      pageRegion = pageRegionMatch.group()
    else:
      pageRegion = page
    linkMatchIter =self.linkRex.finditer(pageRegion)
    for linkMatch in linkMatchIter:
      linkMatchGroupDict = linkMatch.groupdict()
      link = linkMatchGroupDict['href']
      link = self.get_full_link(link, cascadePage.cascadeLink.link)
      entityName = linkMatchGroupDict['entity_name']
      tmpCascadeLink = CascadeLink(link, cascadePage.cascadeLink.cascadeEntityName)
      tmpCascadeLink.cascadeEntityName.names.append(entityName)
      cascadeLinkArray.append(tmpCascadeLink)
    return cascadeLinkArray

  def isNeeded(self, cascadeLink):
    if len(cascadeLink.cascadeEntityName.names) > self.deepLevel:
      return False
    else:
      return True

  def get_savePath(self, cascadeLink):
    if len(cascadeLink.cascadeEntityName.names) == 0:
      return None
    path = self.prefix
    for cascadeEntityName in cascadeLink.cascadeEntityName[:]:
      path += '/'+cascadeEntityName
      if not os.path.exists(path):
        os.mkdir(path)
    path = path + '/' + self.filenameFilter(cascadeLink.cascadeEntityName[-1]) + '.html'
    return path

  def save_page(self, cascadePage):
    path = self.get_savePath(cascadePage.cascadeLink)
    if path and (not os.path.exists(path)) and (not cascadePage.page):
      open(path, 'w').write(cascadePage.page)

  def isPageSaved(self, cascadeLink):
    return os.path.exists(self.get_savePath(cascadeLink))

  def run(self, cascadeLink):
    if self.isNeeded(cascadeLink):
      for name in cascadeLink.cascadeEntityName.names:
        print(name.decode('utf-8'), end='\t')
      print('')
      page = self.get_page(cascadeLink.link)
      cascadePage = CascadePage(page, cascadeLink)
      self.save_page(cascadePage)
      return self.extract_links(cascadePage)

class CrawlerThread(MyThread):
  def run(self):
    while True:
      try:
        callable, args, kwargs = self.workQueue.get(timeout=self.timeout)
        res = callable(*args, **kwargs)
        if not res:
          continue
        for x in res:
          self.workQueue.put((callable, [x], {}))
      except Queue.Empty:
        break
      except :
        print('CrawlerThread')    
        print(sys.exc_info())
        raise

class CrawlerThreadPool(ThreadPool):
  def __init__(self, *args, **kwargs):
    kwargs['Thread']=CrawlerThread
    super(CrawlerThreadPool, self).__init__(*args, **kwargs)

class CascadePage():
  def __init__(self, page, cascadeLink):
    self.page = page
    self.cascadeLink = cascadeLink

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
