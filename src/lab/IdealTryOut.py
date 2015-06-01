'''
Created on 4 May 2013

@author: abednarski
'''

from multiprocessing import Process, Queue
import time

class Task:
    
    def __init__(self, id, click, doubleClick, hold):
        self.id = id
        self.click = click;
        self.doubleClick = doubleClick
        self.hold = hold
    
    def __str__(self):
        return self.id


class Worker:
    
    def __init__(self, workerQueue):
        self.workerQueue = workerQueue
        print "worker - init"
        
    def process(self):
        while True:
            time.sleep(1.5)
            job = self.workerQueue.get()
            print "worker - process: " + str(job)
            if job == 0:
                break
        print "worker - finish"


class Processor:
    
    def __init__(self, processorQueue, workerQueue):
        self.processorQueue = processorQueue       
        self.workerQueue = workerQueue
        print "processor - init"
        
    def process(self):
        while True:
            time.sleep(1)
            task = self.processorQueue.get()
            print "processor - process = " + str(task)
            self.workerQueue.put(task * 2)
            if task == -1:
                break
        print "processor - finish"
                
class Generator:
    
    def __init__(self, outputQueue):
        self.outputQueue = outputQueue
        print "generator - init"
        
    def process(self):
        for task in range(5,-2,-1):
            time.sleep(0.5)
            print "generating - process: " + str(task)
            self.outputQueue.put(task)
        print "generator - finish"
        
if __name__ == '__main__':
    
    print "main - init"
    
    ''' initialize '''
    communicationQueue1 = Queue()
    communicationQueue2 = Queue()
    generator = Generator(communicationQueue1)
    processor = Processor(communicationQueue1, communicationQueue2)
    worker = Worker(communicationQueue2)
    
    ''' detach from current thread'''
    generatorProcess = Process(target = generator.process)
    processorProcess = Process(target = processor.process)
    workerProcess = Process(target = worker.process)
    
    ''' postpone to the very end of main method'''
    workerProcess.start()
    processorProcess.start()
    generatorProcess.start()
        
    print "main - finish"

