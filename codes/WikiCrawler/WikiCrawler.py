#!/usr/bin/python
# coding:utf-8
import os
import sys

sys.path.insert(0,os.environ['MorphMap_HOME']+'/codes/myUtils')
from ThreadPool import ThreadPool, MyThread

from copy import deepcopy
import urllib
import re

class WikiCrawler():
  regionRex = re.compile(r'(?s)<div id="content" class="mw-body" role="main">.*?</div>(?=\s*<div id="mw-navigation">)')
  linkRex = re.compile(r'<a[^>]*?href="(?P<href>[^"]*)"(?:(?!/>).)*?>\s*(?!<)(?P<entity_name>.*?)</a>')
  deepLevel = 3
  prefix = '/home/taoyuchao/MorphMap/output'

  def get_page(self, link):
    html = ""
    try:
      conn = urllib.urlopen(link)
      page = conn.read()
    except:
      print(sys.exc_info())
    return page

  def extract_links(eslf, cascadePage):
    cascadeLinkArray = []
    page = cascadePage.page
    pageRegionMatch = regionRex.search(page)
    if pageRegion:
      pageRegion = pageRegionMatch.group()
    else:
      pageRegion = page
    linkMatchIter = linkRex.finditer(pageRegion)
    for linkMatch in linkMatchIter:
      linkMatchGroupDict = linkMatch.groupdict()
      link = linkMatchGroupDict('href')
      entityName = linkMatchGroupDict('entity_name')
      tmpCascadeLink = CascadeLink(link, cascadePage.cascadeEntityName)
      tmpCascadeLink.cascadeEntityName.append(entityName)
      cascadeLink_array.append(tmpCascadeLink)
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
    if len(cascadeLink.cascadeEntityName) > self.deepLevel:
      return False
    else:
      return True

  def run(self, cascadeLink):
    if isNeeded(cascadeLink):
      page = self.get_page(cascadeLink.link)
      cascadePage = CascadePage(page, cascadeLink.cascadeEntityName)
      self.save_page(cascadePage)
      return self.extract_links(cascadePage)

class CrawlerThreadPool(ThreadPool):
  def __init__(self, *args, **kwargs):
    MyThread = CrawlerThread
    ThreadPool.__init__(*args, **kwargs)

class CrawlerThread(MyThread):
  def run(self):
    while True:
      try:
        callable, args, kwargs = self.workQueue.get(timeout=self.timeout)
        res = callable(*args, **kwargs)
        self.workQueue.put((callable, res, {}))
      except Queue.Empty:
        break
      except :
        print(sys.exc_info())
        raise

class CascadePage():
  def __init__(self, page, cascadeEntityName):
    self.page = page
    self.cascadeEntityName = deepcopy(cascadeEntityName)

class CascadeLink():
  def __init__(self, link, cascadeEntityName):
    self.link = link
    self.cascadeEntityName = deepcopy(cascadeEntityName)

class CascadeEntityName():
  def _init__(self, names):
    self.names = list(names)

if __name__ == '__main__':
  wikiCrawler = WikiCrawler()
  wikiCrawler.run(CascadeLink('https://zh.wikipedia.org/wiki/%E8%96%84%E7%86%99%E6%9D%A5',CascadeEntityName(['薄熙来']))
