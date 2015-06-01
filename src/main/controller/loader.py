class Loader:
    
    def __init__(self):
        self.modulesCache = {}
        self.classesCache = {}
        self.methodsCache = {}
        
    def findModuleByName(self, moduleName):
        module = None
        if(self.modulesCache.has_key(moduleName)):
            module = self.modulesCache[moduleName]
        else:
            module = __import__(moduleName)
            components = moduleName.split('.')
            for comp in components[1:]:
                module = getattr(module, comp)
            self.modulesCache[moduleName] = module
        return module
    
    def findClassInstanceByName(self, moduleName, className):
        classInstance = None        
        cacheKey = moduleName + "." + className
        if(self.classesCache.has_key(cacheKey)):
            classInstance = self.classesCache[cacheKey]        
        else:
            module = self.findModuleByName(moduleName)
            clazz = getattr(module, className)
            classInstance = clazz()
            self.classesCache[cacheKey] = classInstance
        return classInstance
    
    def findMethodInstanceByName(self, moduleName, className, methodName):
        methodInstance = None
        cacheKey = moduleName + "." + className + "." + methodName            
        if(self.methodsCache.has_key(cacheKey)):
            methodInstance = self.methodsCache[cacheKey]
        else:
            classInstance = self.findClassInstanceByName(moduleName, className)
            methodInstance = getattr(classInstance, methodName)
            self.methodsCache[cacheKey] = methodInstance
        return methodInstance