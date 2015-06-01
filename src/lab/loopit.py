'''
Created on 18 Apr 2013

@author: abednarski
'''
'''import Queue
from threading import Thread

def do_work(item):
    print item
    
def worker():
    print "up"


t = Thread(target=worker)
t.daemon = True
t.start()
t.join()'''
from multiprocessing import Process, Pipe
import time

def f(conn):
    message = "z"
    while(message != "x"):
        message = conn.recv()
        print "waiting ..."
        print message
        print "sleeping..."
        time.sleep(1)
    print "bye !"        
    #conn.close()

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=f, args=(child_conn,))
    p.start()
    parent_conn.send("a")
    parent_conn.send("b")
    parent_conn.send("c")
    parent_conn.send("d")
    print "nap !"
    time.sleep(10)
    parent_conn.send("x")
    p.join()
    
    