'''
Created on 18 Mar 2013

@author: abednarski
'''
from main.controller.loader import Loader
import unittest
import sys

class LoaderTest(unittest.TestCase):
    
    __test__ = True
    
    def setUp(self):
        self.classLoader = Loader()
        # swap last two paths to change the class search order    
        lastPathEntry = sys.path.pop()
        sys.path.append("../../main/controller/")
        sys.path.append(lastPathEntry)
    
    def testLoadMyClass(self):
        method = self.classLoader.findMethodInstanceByName("test.controller.my_test_module", "MyTestClass", "myTestMethod")
        self.assertNotEqual(None, method, "Method is not populated.")        
    
    def testLoadMyClass2(self):
        method = self.classLoader.findMethodInstanceByName("test.controller.package.my_test_module_2", "MyTestClass2", "myTestMethod2")
        self.assertNotEqual(None, method, "Method 2 is not populated.")   
        method()
        
    def testLoadVolumeControllerAction(self):
        method = self.classLoader.findMethodInstanceByName("main.controller.volume.volume_controller", "VolumeController", "volumeUp")
        self.assertNotEqual(None, method, "Method should be initiated")                

    def testLoadShellControllerAction(self):
        method = self.classLoader.findMethodInstanceByName("main.controller.shell.shell_controller", "ShellController", "executeCommand")
        self.assertNotEqual(None, method, "Method should be initiated")
        
if __name__ == '__main__':
    unittest.main()