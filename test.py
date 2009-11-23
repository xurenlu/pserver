#!/home/renlu/bin/bin/python
#coding:utf-8
__usage__ = "%prog -n <num>"
__version__ = "$Id: server.py 28 2008-11-03 21:05:15Z matt@ansonia01.com $"
__author__ = "Matt Kangas <matt@daylife.com>"
import sys,os
print sys.path
#from phprpc import PHPRPC_Server # 引入 PHPRPC Server
from phprpc.phprpc import PHPRPC_WSGIApplication, UrlMapMiddleware, PHPRPC_Server
import datetime
from pymmseg import mmseg
import xappy
from flup.server.fcgi import WSGIServer
import optparse

#FCGI_LISTEN_ADDRESS = ('localhost', 9000)
FCGI_SOCKET_DIR = '/tmp'
FCGI_SOCKET_UMASK = 0111

mmseg.dict_load_defaults()

'''
#create_index( "./datadir/", ["text"], ["author","desc","text","categoryid"], ["categoryid"])
#index_data("./datadir/", "book3", { "author":"xurenlu", "desc":"这是一本好书", "text":"故事发生在20年以前", "categoryid":123 },["desc","text"])
#index_data("./datadir/", "book2", { "author":"xurenlu", "desc":"好书不多见", "text":"故事很不错哟12块钱", "categoryid":12},["desc","text"])
report=search_result_report("./datadir/","故事")
print(report)
sout=(search("./datadir/","故事",0,10))
print(sout)
for item in sout:
    for key in item.data:
        print key,":",item.data[key][0]
'''
#分词..
def cnseg(string):
    algor = mmseg.Algorithm(string)
    return " ".join([c.text for c in algor])
#print cnseg("哈哈，我是一只小小鸟")
#sys.exit()
def create_index(dbpath,fulltext_fields,store_fields,index_fields):
    """Create a new index, and set up its field structure.
    """
    try:
        iconn = xappy.IndexerConnection(dbpath)
        for f in fulltext_fields:
            iconn.add_field_action(f,xappy.FieldActions.INDEX_FREETEXT)
        for f in store_fields:
            iconn.add_field_action(f, xappy.FieldActions.STORE_CONTENT)
        for f in index_fields:
            iconn.add_field_action(f, xappy.FieldActions.INDEX_EXACT)
        iconn.close()
        return True
    except:
        return None
def simple_create_index(dbpath):
    return create_index(dbpath,["text"],["text"],[])

def index_data(dbpath,key,data,need_seg_fields):
    """Index a data."""
    try:
        iconn=xappy.IndexerConnection(dbpath)
        doc = xappy.UnprocessedDocument()
        for field in data:
            if field in need_seg_fields:
                doc.fields.append(xappy.Field(field, cnseg(str(data[field]))))
            else:
                doc.fields.append(xappy.Field(field, str(data[field])))
        doc.id=key
        iconn.add(doc)
        iconn.close()
        return {"code":200}
    except Exception,e:
        return {"code":500,"msg":str(e)} 
def simple_index_data(dbpath,key,text):
    return index_data(dbpath,key,{"text":text},["text"])
def count(dbpath):
    sconn = xappy.IndexerConnection(dbpath)
    temp=sconn.get_doccount()
    sconn.close()
    return temp

def search_result_report(dbpath,search):
    """search from database"""
    sconn =  xappy.SearchConnection(dbpath)
    q = sconn.query_parse(search, default_op=sconn.OP_AND)
    results = sconn.search(q,0,0)
    temp ={
            "startrank":results.startrank,
            "endrank":results.endrank,
            "more_matches":results.more_matches,
            "matches_lower_bound":results.matches_lower_bound,
            "matches_upper_bound":results.matches_upper_bound,
            "matches_estimated":results.matches_estimated,
            "estimate_is_exact":results.estimate_is_exact
            }
    sconn.close()
    return temp
def search(dbpath,search,start,limit):
    sconn =  xappy.SearchConnection(dbpath)
    q = sconn.query_parse(search, default_op=sconn.OP_AND)
    results = sconn.search(q,start,limit)
    sconn.close()
    return [result.id for result in results]
def get_document(dbpath,id):
    iconn=xappy.IndexerConnection(dbpath)
    try:
        temp=iconn.get_document(id)
    except:
        return -1
    iconn.close()
    ret={}
    for key in temp.data:
       ret[key]=temp.data[key][0] 
    return {
            "id":temp.id,
            "data":ret
            }
def simple_get_document(dbpath,id):
    val=get_document(dbpath,id)
    return {"id":val["id"],"text":val["data"]["text"]}
def del_document(dbpath,id):
    iconn=xappy.IndexerConnection(dbpath)
    temp=iconn.delete(id)
    iconn.close()
    return temp
#server = PHPRPC_Server("localhost",8090)






def get_socketpath(name, server_number):
    return os.path.join(FCGI_SOCKET_DIR, 'fcgi-%s-%s.socket' % (name, server_number))

def main(args_in, app_name="api"):
    p = optparse.OptionParser(description=__doc__, version=__version__)
    p.set_usage(__usage__)
    p.add_option("-v", action="store_true", dest="verbose", help="verbose logging")
    p.add_option("-n", type="int", dest="server_num", help="Server instance number")
    opt, args = p.parse_args(args_in)

    if not opt.server_num:
        opt.server_num=1

    socketfile = get_socketpath(app_name, opt.server_num)
    app=PHPRPC_WSGIApplication()
    app.add(cnseg)
    app.add(create_index)
    app.add(search)
    app.add(search_result_report)
    app.add(count)
    app.add(index_data)
    app.add(get_document)
    app.add(del_document)
    app.add(simple_get_document)
    app.add(simple_create_index)
    app.add(simple_index_data)
    #app.debug = True
    #app.start()

    try:
        WSGIServer(app,
               bindAddress = socketfile,
               umask = FCGI_SOCKET_UMASK,
               multiplexed = True,
               ).run()
    except Exception,e:
        print 'run app error:"',e
    finally:
        # Clean up server socket file
        if os.path.exists(socketfile):
            os.unlink(socketfile)

#db="./datadir/"
#create_index( db, ["text"], ["author","desc","text","categoryid"], ["categoryid"])
#index_data(db, "book3", { "author":"xurenlu", "desc":"这是一本好书", "text":"故事发生在20年以前", "categoryid":123 },["desc","text"])
#index_data(db, "book2", { "author":"xurenlu", "desc":"好书不多见", "text":"故事很不错哟12块钱", "categoryid":12},["desc","text"])
#report=search_result_report("./datadir/","故事")
#print(report)
#sout=(search("./datadir/","故事",0,10))
#print(sout)
db="./books"
create_index(db, ["text","name","author"], ["author","text","name"], [])
key="b1001"
data={"text":"I am a good student","author":"renlu","name":"new book 1"}
index_data(db,key,data,["text"])
key="b1002"
data={"text":"我是一只小小鸟","author":"renlu","name":"cate1"}
index_data(db,key,data,["text"])
j=get_document(db,key)
print j["data"]["text"]
print search(db,"text:good",0,20)
print search(db,"good",0,20)
print search(db,"text:我是",0,20)
