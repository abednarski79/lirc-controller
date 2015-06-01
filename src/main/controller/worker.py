'''
Created on 8 May 2013

@author: abednarski
'''
import logging

class Job:
    
    def __init__(self, buttonId, actionType):
        self.buttonId = buttonId
        self.actionType = actionType
    
    def __str__(self):
        return self.buttonId + ", " + self.actionType
    
        
class Worker:
    
    def __init__(self, configuration, workerQueue):
        self.workerQueue = workerQueue
        self.mapping = configuration.buttons
        self.cache = configuration.cache
        self.logger = logging.getLogger("worker")
    
    def loop(self):
        self.logger.info("Starting up.")
        self.logger.info("Started.")
        while True:
            job = self.workerQueue.get()
            if job is None:
                self.logger.info("Shutdown signal received.")
                break            
            self.onEvent(job)        
    
    def onEvent(self, job):
        jobId = job.taskUniqueKey()
        jobParameter = job.parameter
        self.logger.debug("New job received: %s with parameter: %s" % (jobId, jobParameter))
        if jobId not in self.cache:
            self.logger.warning("No task with id: %s in cache: %s" % jobId, self.cache);
            return        
        self.logger.debug("Cache contains method: %s" % jobId)
        method = self.cache[jobId]
        if method is None:
            self.logger.warning("Method is missing: %s" % jobId)
            return
        self.logger.info("Executing job: %s with parameter: %s" % (jobId, jobParameter))
        try:
            method(job.parameter)
        except Exception as details:
            self.logger.error("Can't run method %s, details: %s" % (jobId, details))
    
    def shutdown(self):
        self.logger.info("Shutting down.")        
        self.workerQueue.put_nowait(None)
            