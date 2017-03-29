#!/usr/bin/python
# coding:utf-8
import threading
import Queue

import sys
import time
import urllib

class MyThread(threading.Thread):
 def __init__(self, workQueue, resultQueue,timeout, **kwargs):
  threading.Thread.__init__(self, kwargs=kwargs)
  #线程在结束前等待任务队列多长时间
  self.timeout = timeout
  self.setDaemon(True)
  self.workQueue = workQueue
  self.resultQueue = resultQueue
  self.start()

 def run(self):
  while True:
   try:
    #从工作队列中获取一个任务
    callable, args, kwargs = self.workQueue.get(timeout=self.timeout)
    #我们要执行的任务
    res = callable(*args, **kwargs)
    #报任务返回的结果放在结果队列中
    self.resultQueue.put({'result':res, 'thread_name':self.getName()})    
   except Queue.Empty: #任务队列空的时候结束此线程
    break
   except :
    print(sys.exc_info())
    raise

class ThreadPool(object):
 def __init__( self, num_of_threads=10, timeout=1, Thread=MyThread):
  self.workQueue = Queue.Queue()
  self.resultQueue = Queue.Queue()
  self.threads = []
  self.timeout = timeout
  self.Thread = Thread
  self.__createThreadPool( num_of_threads )

 def __createThreadPool( self, num_of_threads ):
  for i in range( num_of_threads ):
   thread = self.Thread( self.workQueue, self.resultQueue, self.timeout )
   self.threads.append(thread)

 def wait_for_complete(self):
  #等待所有线程完成。
  while len(self.threads):
   thread = self.threads.pop()
   #等待线程结束
   if thread.isAlive():#判断线程是否还存活来决定是否调用join
    thread.join()
    
 def add_job( self, callable, *args, **kwargs ):
  self.workQueue.put( (callable,args,kwargs) )


def test_job(id, sleep = 0.001 ):
 html = ""
 try:
  conn = urllib.urlopen('http://www.baidu.com/')
  html = conn.read(20)
 except:
  print(sys.exc_info())
 return  html

def test():
 print('start testing')
 tp = ThreadPool(10)
 for i in range(5):
  time.sleep(0.2)
  tp.add_job( test_job, i, i*0.001 )
 tp.wait_for_complete()
 #处理结果
 print('result Queue\'s length == %d '% tp.resultQueue.qsize())
 while tp.resultQueue.qsize():
  print(tp.resultQueue.get())
 print('end testing')

if __name__ == '__main__':
 test()
