'''
Created on 23 Jun 2013

@author: abednarski
'''

import signal, os, time, sys
from multiprocessing import Process, Queue

processes = []

def shutdown(signum, frame):
    f = open('/tmp/log_parent.txt', 'w')
    sys.stdout = f
    print "Shutting down ..."
    for process in processes:
        print "Killing process: %s" % (process.name)
        process.terminate()
        process.join()
    print "Exiting."
    f.flush()
    exit(0)

def run():
    i = 0    
    f = open('/tmp/log_child.txt', 'w')
    sys.stdout = f
    while True:
        i = i + 1
        print "Still alive ! %s" % i
        f.flush() 
        time.sleep(0.25)

if __name__ == '__main__':    
    signal.signal(signal.SIGTERM, shutdown)  
    myProcess = Process(target = run, name = "myProcess")    
    processes.append(myProcess)
    myProcess.start()
    myProcess.join()     
    
