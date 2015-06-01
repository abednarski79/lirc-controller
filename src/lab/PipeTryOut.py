from multiprocessing import Process, Pipe
import time

class Executor:
    def __init__(self, subConn):
        self.subConn = subConn
    def execute(self):
        command = 0
        while(command != 9):
            command = self.subConn.recv()
            time.sleep(2)
            print "executing: " + str(command)
        print "terminating executor."
        
class Processor:
    def __init__(self, procConn):
        self.procConn = procConn
        self.parent_conn, child_conn = Pipe()        
        executor = Executor(child_conn)
        self.subProcess = Process(target=executor.execute)
        self.subProcess.start()  
    def process(self):
        data = 0
        while(data != 10):
            data = self.procConn.recv()        
            time.sleep(1)
            print "processing: " + str(data)
            self.parent_conn.send(data)
        print "terminating processor."

class Generator:
    def __init__(self, genConn):
        self.genConn = genConn
        pass
    def generate(self):
        for num in range(1,11):
            print "sending: " + str(num)
            self.genConn.send(num)        
    
class MainRunner:
    def __init__(self):
        parent_conn, child_conn = Pipe()
        self.generator = Generator(parent_conn)
        processor = Processor(child_conn)
        self.process = Process(target=processor.process)
    def run(self):
        self.process.start()
        self.generator.generate()


if __name__ == '__main__':
    runner = MainRunner()
    runner.run()
    