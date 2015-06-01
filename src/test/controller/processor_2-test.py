'''
Created on 11 Mar 2012

@author: abednarski
'''
from main.controller.configuration import Configuration, Button, Action
from main.controller.processor_2 import Processor, Event
import time
import unittest
from multiprocessing import Queue, JoinableQueue
from main.controller.worker import Job
    
class ProcessorTest(unittest.TestCase):
    
    __test__ = True
    
    actionDelayFactor = 1.1
    testDelayFactor = 1.2    
    
    def setUp(self):
        print "Setup processor"
        self.gapDuration = 1
        self.sleepDuration =   self.gapDuration * self.testDelayFactor
        blocking = False
        # button - PLUS
        # all types of usage should results in this same task
        plusAction = Action("plus-id", "plus-task", isCancelable = False)
        self.plusButton = Button("PLUS-BUTTON", plusAction, plusAction, plusAction)        
        # button - FORWARD
        # when clicked once then next song should be played, when double-clicked then next album should be played 
        # and when hold then next play-list should be played 
        nextSongAction = Action("next-song-id", "next-song-task", fireDelay = (self.gapDuration * self.actionDelayFactor))
        nextAlbumAction = Action("next-album-id", "next-album-task", fireDelay = (self.gapDuration * self.actionDelayFactor))
        nextPlaylistAction = Action("next-playlist-id", "next-playlist-task", minimalRepeatTrigger = 1)
        self.forwardButton = Button("FORWARD-BUTTON", nextSongAction, nextAlbumAction, nextPlaylistAction)      
        # button - MENU
        # when clicked once then general mode menu task should be executed, when hold current mode menu task should be executed
        globalModeAction = Action("global-menu-id", "global-menu-task", fireDelay = (self.gapDuration * self.actionDelayFactor))
        currentMenuAction = Action ("current-menu-id", "current-menu-task", minimalRepeatTrigger = 1)
        self.menuButton = Button("MENU-BUTTON", globalModeAction, globalModeAction, currentMenuAction)
        # button - PLAY
        # when clicked once then play/pause task should be executed, when hold for at least 5 rounds power off task should be executed
        playPauseAction = Action("play-pause-id", "play-pause-task", fireDelay = (self.gapDuration * self.actionDelayFactor))
        powerOffAction = Action("power-off-id", "power-off-task", minimalRepeatTrigger = 5)
        self.playButton = Button("PLAY-BUTTON", playPauseAction , playPauseAction, powerOffAction)
        # configuration
        buttons = {}
        buttons[self.plusButton.id] = self.plusButton
        buttons[self.forwardButton.id] = self.forwardButton
        buttons[self.menuButton.id] = self.menuButton
        buttons[self.playButton.id] = self.playButton  
        self.processorQueue = Queue()
        self.actualWorkerQueue = Queue()
        self.expectedWorkerQueue = Queue()
        # processor        
        self.processor = Processor(buttons, self.processorQueue, self.actualWorkerQueue)

    def convetQueueToList(self, queue):
        list = []
        while not queue.empty():
            element = queue.get()
            # queue.task_done()
            list.append(element)
        return list
    
    def validateQueuesEquality(self, message = None):
        expectedWorkerList = self.convetQueueToList(self.expectedWorkerQueue)
        expectedWorkerList.sort()        
        actualWorkerList = self.convetQueueToList(self.actualWorkerQueue)
        actualWorkerList.sort()
        print "expectedWorkerList: %s" % expectedWorkerList
        print "actualWorkerList: %s" % actualWorkerList
        self.assertEqual(actualWorkerList, expectedWorkerList, message)
    
    def tearDown(self):
        self.processor= None
        self.configuration = None

    def clickButton(self, button, repeat):
        ''' Simulates button click on the remote '''
        print "Clicking button: %s repeat %s." % (button.id, repeat)
        self.processorQueue.put(Event(button.id, repeat))
    
    def storeJob(self, button, type):
        self.expectedWorkerQueue.put(Job(button.id, type))
    
    def putTerminationSignal(self, queue):
        # self.processorQueue.put(None)
        queue.put(None)
    
    def sleep(self):
        print "Going to sleep for %s seconds ..." % self.sleepDuration
        time.sleep(self.sleepDuration)
    
    def runProcessor(self):
        self.putTerminationSignal(self.processorQueue)
        self.putTerminationSignal(self.expectedWorkerQueue)
        self.processor.loop()
        self.sleep()
        
    def testPlusButtonClick(self):        
        self.clickButton(self.plusButton, 0)
        self.expectedWorkerQueue.put(self.plusButton.click.task) 
        self.runProcessor()
        self.validateQueuesEquality()
                             
    def testPlusButtonDoubleClick(self):        
        self.clickButton(self.plusButton, 0)
        self.expectedWorkerQueue.put(self.plusButton.click.task)
        self.clickButton(self.plusButton, 0)
        self.expectedWorkerQueue.put(self.plusButton.click.task)            
        self.runProcessor()
        self.validateQueuesEquality();        
    
    def testPlusButtonHold(self):
        self.clickButton(self.plusButton, 0)
        self.expectedWorkerQueue.put(self.plusButton.click.task)
        self.clickButton(self.plusButton, 1)
        self.expectedWorkerQueue.put(self.plusButton.click.task)
        self.clickButton(self.plusButton, 2)
        self.expectedWorkerQueue.put(self.plusButton.click.task)
        self.runProcessor()
        self.validateQueuesEquality() 
    
    def testForwardButtonClick(self):
        self.clickButton(self.forwardButton, 0)
        self.expectedWorkerQueue.put(self.forwardButton.click.task)
        self.runProcessor()      
        self.validateQueuesEquality() 
            
    def testForwardButtonDoubleClick(self):
        '''
        Scenario:
        Forward button was clicked twice in very short period of time.
        It is expected that only the double-click task will be present in the worker queue and the single-click task will be ignored.
        '''        
        self.clickButton(self.forwardButton, 0)        
        self.clickButton(self.forwardButton, 0)
        self.expectedWorkerQueue.put(self.forwardButton.doubleClick.task)
        self.runProcessor()
        self.validateQueuesEquality("Should contain only next album task")

    def testForwardButtonHold(self):
        '''
        Scenario: 
        Forward button was held.
        Expectations:
        Only the hold task associated with this button will be present in the worker queue.
        '''        
        self.clickButton(self.forwardButton, 0)
        self.clickButton(self.forwardButton, 1)
        self.expectedWorkerQueue.put(self.forwardButton.hold.task)
        self.runProcessor()     
        self.validateQueuesEquality("Should contain only next playlist task");

    def testMenuButtonClick(self):
        '''
        Scenario: 
        Menu button was clicked once.
        Expectations:
        Only the single-click task associated with this button will be present in the worker queue.
        '''
        self.clickButton(self.menuButton, 0)
        self.expectedWorkerQueue.put(self.menuButton.click.task)
        self.runProcessor()
        self.validateQueuesEquality("Should contain only 1x global menu task");
    
    def testMenuDoubleButtonClick(self):
        '''
        Scenario:
        Menu button was clicked twice in quick succession.
        Expectations:
        Only double-click menu task should be present in worker queue. 
        '''
        self.clickButton(self.menuButton, 0)
        self.clickButton(self.menuButton, 0)
        self.expectedWorkerQueue.put(self.menuButton.doubleClick.task)
        self.runProcessor()
        self.validateQueuesEquality("Should contain only 1x global menu task");
        
    def testMenuHold(self):
        '''
        Scenario:
        Menu button was hold.
        Expectations:
        Only hold menu task should be present in worker queue. 
        '''
        self.clickButton(self.menuButton, 0)
        self.clickButton(self.menuButton, 1)
        self.expectedWorkerQueue.put(self.menuButton.hold.task)
        self.runProcessor()
        self.validateQueuesEquality("Should contain only 1x current menu task");
        
    def testPlayButtonClick(self):
        '''
        Scenario:
        Play button was clicked once.
        Expectations:
        One click taks should be present in the worke queu. 
        '''        
        self.clickButton(self.playButton, 0)
        self.expectedWorkerQueue.put(self.playButton.click.task)
        self.runProcessor()
        self.validateQueuesEquality("Should contain only 1x play-pause task");
    
    def testPlayButtonDoubleClick(self):
        '''
        Scenario:
        Play button was clicked once.
        Expectations:
        It is expected that just one task (double or single click) will be present in the worker queue.
        The reason behind that is that button is configured in the way that previous unfinished task
        is cancelled if another one is stored in the queue see: button.isCancelable
        '''
        self.clickButton(self.playButton, 0)
        self.clickButton(self.playButton, 0)
        self.expectedWorkerQueue.put(self.playButton.click.task)
        self.runProcessor()
        self.validateQueuesEquality("Should contain only 1x play-pause task");
        
    def testPlayButtonHoldx1(self):
        '''
        Scenario:
        Play button was held (for 2 rounds).
        Expectations:
        Expected no task to be present in worker queue as minimal repeats trigger of 5 was not met.
        '''
        self.clickButton(self.playButton, 0)
        self.clickButton(self.playButton, 1)
        self.runProcessor()
        self.validateQueuesEquality("Should be empty");
    
    def testPlayButtonHoldx5(self):
        '''
        Scenario:
        Play button was held for long time (for 6 rounds).
        Expectations:
        Expected hold task to be present in worker queue as minimal repeats trigger of 5 was met.
        '''
        self.clickButton(self.playButton, 0)
        self.clickButton(self.playButton, 1)
        self.clickButton(self.playButton, 2)
        self.clickButton(self.playButton, 3)
        self.clickButton(self.playButton, 4)
        self.clickButton(self.playButton, 5)
        self.expectedWorkerQueue.put(self.playButton.hold.task)
        self.runProcessor()
        self.validateQueuesEquality("Should contain only 1x power-off task");
        
    def testForwardButtonDoubleClickAndMenuButtonClick(self):
        '''
        Scenario:
        Forward button was clicked twice in very short period of time. Just after that
        menu button was clicked once.
        Expectations:
        It is expected that 2 tasks will be present in worke queue: 
        - double-click forward task
        AND
        - click menu task 
        Note (1) that single-click forward task will be ignored.
        Note (2) that both buttons were configured to be cancelable (isCancelable is by default set to TRUE)
        '''        
        self.clickButton(self.forwardButton, 0)        
        self.clickButton(self.forwardButton, 0)
        self.clickButton(self.menuButton, 0)
        self.expectedWorkerQueue.put(self.forwardButton.doubleClick.task)
        self.expectedWorkerQueue.put(self.menuButton.click.task)
        self.runProcessor()
        self.validateQueuesEquality("Should contain next album task and menu click task")
          
if __name__ == "__main__":
    unittest.main()
