
import pylirc
import select
import Queue
import logging
from multiprocessing.synchronize import Event

class GeneratorEvent():
    def __init__(self, key, repeat):
        self.key = key
        self.repeat = repeat
        
class Generator():
    
    def __init__(self, configurationPath, outputQueue):
        self.processorQueue = outputQueue
        self.logger = logging.getLogger("generator")
        self.lirchandle = pylirc.init("pylirc", configurationPath, False)
        self.stopFlag = Event()

    def loop(self):
        self.logger.info("Starting up.")
        if(self.lirchandle):
            inputLirc = [self.lirchandle]
            timeout = 2
            self.logger.info("Succesfully opened lirc, handle is " + str(self.lirchandle))
            self.logger.info("Started.")
            while (not self.stopFlag.is_set()):
                inputready, outputready, exceptready = select.select(inputLirc,[],[], timeout)
                s = pylirc.nextcode(1)                    
                if(s):
                    for code in s:                        
                        repeat = code["repeat"]
                        currentCommand = code["config"]
                        self.logger.info("New event received: id: = %s, repeat = %s" % (currentCommand, repeat))
                        try:                            
                            self.processorQueue.put_nowait(GeneratorEvent(currentCommand, repeat))
                        except Queue.Full:
                            self.logger.error("Processor queue is overloaded.")                    
            self.logger.info("Shutted down.")

    def shutdown(self):
        self.logger.debug("Shutting down.")        
        self.stopFlag.set()
        pylirc.exit()        