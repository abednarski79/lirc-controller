'''
Created on 14 Apr 2013

@author: abednarski
'''

from main.controller.configuration import ConfigurationReader
from main.controller.generator import Generator
from main.controller.processor_2 import Processor
from main.controller.worker import Worker
from multiprocessing import Process, Queue
from optparse import OptionParser
import sys, signal
import logging
import logging.config

processors = {}

class OptionsParseWrapper:
    def __init__(self, inputData):
        self.inputData = inputData
        
    def parseOptions(self):
        parser = OptionParser()
        parser.add_option("-c", "--conf", 
                          dest="cfg", 
                          action="store",
                          help="configuration from cfg FILE", 
                          metavar="FILE")
        parser.add_option("-x", "--xml", 
                          dest="xml", 
                          action="store",
                          help="configuration from xml FILE", 
                          metavar="FILE")
        parser.add_option("-l", "--log", 
                          dest="log", 
                          action="store",
                          help="configuration from log FILE", 
                          metavar="FILE")        
        (options, args) = parser.parse_args(args=self.inputData)  
        # Making sure all mandatory options appeared.
        mandatories = ['cfg', 'xml', 'log']
        for m in mandatories:
            if not options.__dict__[m]:
                print "Mandatory option %s is missing" % m
                parser.print_help()
                exit(-1)
        return options

def shutdown(signum, frame):
        logger.info("Shutting down ...")
        for processor in processors:
            process = processors[processor]
            logger.info("Stopping processor: %s" % processor.__class__.__name__)
            processor.shutdown()
            process.join()            
        logger.info("Lirc-controller stopped.")
        exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, shutdown)
    optionsParse = OptionsParseWrapper(sys.argv[1:])
    parameters = optionsParse.parseOptions()
    logging.config.fileConfig(parameters.log)
    logger = logging.getLogger("app")
    logger.info("Starting lirc-controller.")    
    configurationReader = ConfigurationReader(parameters.xml)
    configuration = configurationReader.readConfiguration()    
    generatorQueue = Queue()
    workerQueue = Queue()
    generator = Generator(parameters.cfg, generatorQueue)
    processor = Processor(configuration, generatorQueue, workerQueue)
    worker = Worker(configuration, workerQueue)
    generatorProcess = Process(target = generator.loop)
    processorProcess = Process(target = processor.loop)
    workerProcess = Process(target = worker.loop)
    workerProcess.start()
    processorProcess.start()
    generatorProcess.start()    
    processors[worker] = workerProcess
    processors[processor] = processorProcess
    processors[generator] = generatorProcess
    logger.info("Lirc-controller started.")