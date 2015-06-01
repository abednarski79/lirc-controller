'''
Created on 21 Mar 2013

@author: abednarski
'''
import subprocess
import logging

class ShellController():
    
    def __init__(self):
        self.logger = logging.getLogger("worker")
        
    def executeCommand(self, command):
        self.command = command
        self.logger.debug("Running shell command: %s" % self.command)
        subprocess.call(self.command, shell=True)
        
    def __str__(self):
        return "ShellController: command = %s" % (self.command)