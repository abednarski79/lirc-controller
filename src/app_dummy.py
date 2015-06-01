'''
Created on 14 Apr 2013

@author: abednarski
'''

from main.controller.configuration import ConfigurationReader
from main.controller.processor_2 import Processor, GeneratorEvent
from main.controller.worker import Worker
from multiprocessing import Process, Queue
from app import OptionsParseWrapper
import sys
    
if __name__ == '__main__':
    optionsParse = OptionsParseWrapper(sys.argv[1:])    
    parameters = optionsParse.parseOptions()
    configurationReader = ConfigurationReader(parameters.xml)
    configuration = configurationReader.readConfiguration()    
    generatorQueue = Queue()
    workerQueue = Queue()
    # generator = Generator(generatorQueue)
    processor = Processor(configuration, generatorQueue, workerQueue)
    worker = Worker(configuration, workerQueue)
    # generatorProcess = Process(target = generator.loop)
    processorProcess = Process(target = processor.loop)
    workerProcess = Process(target = worker.loop)
    workerProcess.start()
    processorProcess.start()
    # generatorProcess.start()
    generatorQueue.put_nowait(GeneratorEvent("PLUS_ID", 0))
    generatorQueue.put_nowait(GeneratorEvent("MINUS_ID", 0))
