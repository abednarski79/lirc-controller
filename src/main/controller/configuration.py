'''
Created on 11 Mar 2012

@author: abednarski
'''

from main.controller.loader import Loader
import xml.etree.ElementTree as ET
import logging

class Task():    
    def __init__(self, module, clazz, method, parameter):
        self.module = module
        self.clazz = clazz
        self.method = method
        self.parameter = parameter
    
    def taskUniqueKey(self):
        return "%s.%s.%s" % (self.module, self.clazz, self.method)
    
    def __str__(self):
        return "<Task:  module name = " + self.module + ", class name = " + self.clazz + ", method name= " + self.method + ", parameter = " + self.parameter + ">"

    def __cmp__(self, otherTask):
        if(otherTask == None):
            return -1
        if(self.module != otherTask.module):            
            return -1
        if(self.clazz != otherTask.clazz):            
            return -1
        if(self.method != otherTask.method):            
            return -1  
        if(self.parameter != otherTask.parameter):            
            return -1         
        return 0

class ActionType:
    CLICK = "CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    HOLD = "HOLD"
            
class Action():    
    def __init__(self, id, task, fireDelay = 0, isCancelable = True, minimalRepeatTrigger = 0):
        self.id = id
        self.task = task
        self.fireDelay = fireDelay
        self.isCancelable = isCancelable
        self.minimalRepeatTrigger = minimalRepeatTrigger
    
    def __str__(self):
        return "<Action:  id = %s>" % (self.id)
    
    def __cmp__(self, otherAction):
        if(otherAction == None):
            return -1
        if(self.id != otherAction.id):
            return -1
        if(self.task != otherAction.task):
            return -1        
        if(self.fireDelay != otherAction.fireDelay):
            return -1
        if(self.isCancelable != otherAction.isCancelable):
            return -1
        if(self.minimalRepeatTrigger != otherAction.minimalRepeatTrigger):
            return -1    
        return 0


class Button():        
    def __init__(self, id, click = None, doubleClick = None, hold = None):
        self.id = id
        self.click = click
        self.doubleClick = doubleClick
        self.hold = hold
    
    def __str__(self):
        return "<Button: id = %s, click = %s, double click = %s, hold = %s" % (self.id, self.click, self.doubleClick, self.hold) + ">"        
    
    def __cmp__(self, otherButton):
        if(otherButton == None):
            return -1
        if(self.id != otherButton.id):
            return -1
        if(self.click != otherButton.click):
            return -1
        if(self.doubleClick != otherButton.doubleClick):
            return -1
        if(self.hold != otherButton.hold):
            return -1
        return 0
                   
    
class Configuration():    
    def __init__(self, gapDuration, blocking, buttons, cache):
        self.gapDuration = gapDuration
        self.blocking = blocking
        self.buttons = buttons
        self.cache = cache
    
    def __str__(self):
        return "<Configuration: gap duration = %s, blocking = %s, buttons = %s>" % (self.gapDuration, self.blocking, self.buttons)              

class ConfigurationReader:    
    def __init__(self, configurationPath, classLoader = None):
        self.logger = logging.getLogger("app")
        self.configurationPath = configurationPath
        self.buttons = {}
        self.cache = {}
        self.gapDuration = 0
        self.blocking = 0
        if classLoader is None:
            self.classLoader = Loader()
        else:
            self.classLoader = classLoader
        
    def readConfiguration(self):   
                
        self.logger.info("Reading configuration from %s" % self.configurationPath)        
        tree = ET.parse(self.configurationPath)
        root = tree.getroot()
        propertyElements = root.findall('properties/property')
        for propertyElement in propertyElements:
            propertyId = propertyElement.get("id")
            propertyValue = propertyElement.text
            if(propertyId == "gapDuration"):
                self.gapDuration = propertyValue
            elif(propertyId == "blocking"):
                self.blocking = propertyValue
        buttonElements = root.findall('buttons/button')
        for buttonElement in buttonElements:
            buttonId = buttonElement.get("id")
            self.logger.debug("Button configuration: %s" % buttonId)            
            actionElements = buttonElement.findall('action')            
            buttonClick = None
            buttonDoubleClick = None
            buttonHold = None
            for actionElement in actionElements:
                # build task
                taskElement = actionElement.find("task")                
                moduleName = taskElement.find("module").text
                className = taskElement.find("class").text
                methodName = taskElement.find("method").text
                parameter = taskElement.find("parameter").text                 
                task = self.buildTask(moduleName, className, methodName, parameter)                
                # store method instance in the cache
                self.storeMethod(task)                
                # build action
                actionId = actionElement.get("id")
                isCancelableElement = actionElement.find("isCancelable")
                fireDelayElement = actionElement.find("fireDelay")                
                minimalRepeatTriggerElement = actionElement.find("minimalRepeatTrigger")
                action = self.buildAction(actionId, task, isCancelableElement, fireDelayElement, minimalRepeatTriggerElement)
                # assign task to button
                actionType = actionElement.get("type")
                if (actionType == ActionType.CLICK):
                    buttonClick = action
                elif (actionType == ActionType.DOUBLE_CLICK):
                    buttonDoubleClick = action
                else:
                    buttonHold = action            
            button = self.buildButton(buttonId, buttonClick, buttonDoubleClick, buttonHold)
            self.storeButton(button)                
            self.logger.info("New button added: %s" % button)        
        return Configuration(self.gapDuration, self.blocking, self.buttons, self.cache)
    
    def buildButton(self, buttonId, clickAction, doubleClickAction, holdAction):
        button = Button(buttonId)
        button.click = clickAction
        button.doubleClick = doubleClickAction
        button.hold = holdAction
        return button
        
    def buildAction(self, actionId, task, isCancelableElement, fireDelayElement, minimalRepeatTriggerElement):        
        if(isCancelableElement != None):
            if(isCancelableElement.text.lower == "true"):
                isCancelable = True
            else:
                isCancelable = False    
        else:
            isCancelable = True
        if(fireDelayElement != None):
            fireDelay = float(fireDelayElement.text)
        else:
            fireDelay = 0        
        if(minimalRepeatTriggerElement != None):
            minimalRepeatTrigger = int(minimalRepeatTriggerElement.text)
        else:
            minimalRepeatTrigger = 0 
        action = Action(actionId, task, fireDelay, isCancelable, minimalRepeatTrigger)
        return action
    
    def buildTask(self, moduleName, className, methodName, parameter):
        task = Task(moduleName, className, methodName, parameter)
        return task
    
    def storeButton(self, button):
        self.buttons[button.id] = button
        
    def storeMethod(self, task):
        taskUniqueKey = task.taskUniqueKey()
        self.logger.debug("Storing method with key: %s" % taskUniqueKey)        
        if self.cache.has_key(taskUniqueKey):
            self.logger.debug("Method already cached.")
            return
        self.logger.info("New method added: %s" % taskUniqueKey)
        methodInstance = self.classLoader.findMethodInstanceByName(task.module, task.clazz, task.method)                          
        self.cache[taskUniqueKey] = methodInstance

