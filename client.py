#!/usr/bin/python
#coding:utf-8
import sys,os,time
from pymmseg import mmseg
import xappy
sys.path.append("./py24/")
from phprpc.phprpc import PHPRPC_Client  
client = PHPRPC_Client('http://localhost:8020/')  
clientProxy = client.useService()  
print time.time()
print client.cnseg("我是一只小小鸟,我是一只远方孤独的泪水,藏在你心里已几万年")
print time.time()
print(client.search("./data3/","故事",0,10))
print time.time()
d=(client.get_document("./data3/","str3"))
print d
print time.time()
#print d["id"]
#print d["data"]["text"]
#print client.count("./datadir/")
#print(clientProxy.search_result_report("./datadir/","故事"))
#
#print client.search("./datadir/","一本",0,10)
#print client.simple_create_index("./data3/")
#client.simple_index_data("./data3/","str1","我来自东亚")
#client.simple_index_data("./data3/","str2","我来自中国")
#client.simple_index_data("./data3/","str3","我来自东北")
print client.search("./data3/","我",0,10)
#print client.search("./data3/","中国",0,10)
#print client.search("./data3/","东北",0,10)
#print client.simple_get_document("./data3/","str1")["text"]
print time.time()
