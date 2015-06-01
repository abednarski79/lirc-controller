'''
Created on 11 Mar 2012

@author: abednarski
'''
from threading import Timer
import logging
import Queue

class GeneratorEvent():
    def __init__(self, key, repeat):
        self.key = key
        self.repeat = repeat
    def __str__(self):
        return self.key
    
class Processor():
    '''
    Processor
    '''
    
    def __init__(self, configuration, processorQueue, workerQueue):
        self.logger = logging.getLogger("processor")
        self.currentButton = None
        self.activeTimers = {}
        self.mapping = configuration.buttons            
        self.processorQueue = processorQueue
        self.workerQueue = workerQueue
    
    def loop(self):
        self.logger.info("Starting up.")
        self.logger.info("Started.")
        while True:
            event = self.processorQueue.get()
            if event is None:
                self.logger.info("Shutting down.")
                break          
            self.onEvent(event)

    def onEvent(self, event):
        ''' 
        Process single event and executes selected task, where:
        key - name of the key to be processed
        repeat - repeat index number 
        '''
        if(self.mapping.has_key(event.key)):
            currentButton = self.mapping[event.key]
        else:
            self.logger.warning("Button with key %s not present in configuration." % (event.key))            
            return        
        self.logger.info("New event received: id: = %s, repeat = %s" % (currentButton, event.repeat))
        if(event.repeat == 0):
            if(self.isTimerRunning(event.key) == False): 
                '''timer responsible for adding new tasks to execution queue is not running
                this means that this call will be treated as -click- action'''
                self.logger.debug("Timer is not running, processing 'click' task")
                currentAction = currentButton.click
            else:
                '''timer responsible for adding new tasks to execution queue is currently running
                this means that this call will be treated as -double-click- action
                also timer needs to be cancelled (in other case -click- and -double-click- will be processed)'''
                self.logger.debug("Timer is running, processing 'double click' task")                
                self.deleteTimer(event.key)
                currentAction = currentButton.doubleClick
        else:
            '''repeat index > 0 so this same button was hold, this call will be processed as -hold- action
            also in this case timer must be cancelled'''
            self.logger.debug("Button is repeated, processing 'hold' task")            
            self.deleteTimer(event.key)
            currentAction = currentButton.hold
        if(currentAction != None):
            self.addTaskToWorkerQueue(currentAction, event)
        else:
            self.logger.warning("Action for repeat %s not configured for button: %s" % (event.repeat, event.key))
    
    def addTaskToWorkerQueue(self, action, event):
        if(event.repeat < action.minimalRepeatTrigger):
            self.logger.debug("Ignoring task, delay: %s, name: %s, min. repeat trigger: %s" % (action.fireDelay, action.task, action.minimalRepeatTrigger))
            return
        self.logger.debug("Processing task, delay: %s, name: %s, min. repeat trigger: %s" % (action.fireDelay, action.task, action.minimalRepeatTrigger))
        if(action.fireDelay == 0):           
            self.addToWorkerQueueNoWait(action.task, event.key)
        else:
            self.addToWorkerQueueWait(action.fireDelay, self.addToWorkerQueueNoWait, [action.task, event.key], event.key)
        
    def addToWorkerQueueWait(self, executionDelay, methodToExecute, methodParameters, timerId):
        self.logger.debug("Creating timer to call method: %s with parameters: %s in: %s seconds" % (methodToExecute.__name__, methodParameters, executionDelay))
        self.createTimer(executionDelay, methodToExecute, methodParameters, timerId)        
        
    def addToWorkerQueueNoWait(self, action, timerId):
        self.logger.info("Adding action: %s to execution queue" % (action))
        try:
            self.workerQueue.put_nowait(action)
        except Queue.Full():
            self.logger.error("Worker queue is overloaded.");
        self.deleteTimer(timerId)
    
    def isTimerRunning(self, timerId):
        if(self.activeTimers.has_key(timerId)):
            return True
        return False
    
    def createTimer(self, executionDelay, methodToExecute, methodParameters, timerId):
        timer = Timer(executionDelay, methodToExecute, methodParameters)
        timer.start()        
        self.activeTimers[timerId] = timer
    
    def deleteTimer(self, timerId):
        if(self.isTimerRunning(timerId) == False):
            return
        self.logger.debug("Cancelling the timer: %s" % timerId)
        self.activeTimers[timerId].cancel()
        del self.activeTimers[timerId]
        self.logger.debug("Timer: %s cancelled." % timerId)

    def shutdown(self):        
        self.processorQueue.put_nowait(None)
