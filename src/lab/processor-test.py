'''
Created on 11 Mar 2012

@author: abednarski
'''
from main.controller.configuration import Configuration, Button, Action
from main.controller.processor import Processor
import time
import unittest


class ProcessorTest(unittest.TestCase):
    
    __test__ = False
    
    actionDelayFactor = 1.1
    testDelayFactor = 1.2    
    
    def setUp(self):
        print "Setup processor"
        gapDuration = 1
        blocking = False
        # button - PLUS
        # all types of usage should results in this same task
        plusAction = Action("plus-id", "plus-task", isCancelable = False)
        self.plusButton = Button("PLUS-BUTTON", plusAction, plusAction, plusAction)        
        # button - FORWARD
        # when clicked once then next song should be played, when double-clicked then next album should be played 
        # and when hold then next play-list should be played 
        nextSongAction = Action("next-song-id", "next-song-task", fireDelay = (gapDuration * self.actionDelayFactor))
        nextAlbumAction = Action("next-album-id", "next-album-task", fireDelay = (gapDuration * self.actionDelayFactor))
        nextPlaylistAction = Action("next-playlist-id", "next-playlist-task", minimalRepeatTrigger = 1)
        self.forwardButton = Button("FORWARD-BUTTON", nextSongAction, nextAlbumAction, nextPlaylistAction)      
        # button - MENU
        # when clicked once then general mode menu task should be executed, when hold current mode menu task should be executed
        globalModeAction = Action("global-menu-id", "global-menu-task", fireDelay = (gapDuration * self.actionDelayFactor))
        currentMenuAction = Action ("current-menu-id", "current-menu-task", minimalRepeatTrigger = 1)
        self.menuButton = Button("MENU-BUTTON", globalModeAction, globalModeAction, currentMenuAction)
        # button - PLAY
        # when clicked once then play/pause task should be executed, when hold for at least 5 rounds power off task should be executed
        playPauseAction = Action("play-pause-id", "play-pause-task", fireDelay = (gapDuration * self.actionDelayFactor))
        powerOffAction = Action("power-off-id", "power-off-task", minimalRepeatTrigger = 5)
        self.playButton = Button("PLAY-BUTTON", playPauseAction , playPauseAction, powerOffAction)
        # configuration
        buttons = {}
        buttons[self.plusButton.id] = self.plusButton
        buttons[self.forwardButton.id] = self.forwardButton
        buttons[self.menuButton.id] = self.menuButton
        buttons[self.playButton.id] = self.playButton        
        self.configuration = Configuration(gapDuration, blocking, buttons)
        # processor        
        self.processor = Processor(self.configuration)


    def tearDown(self):
        self.processor= None
        self.configuration = None

    def clickButton(self, button, repeat):
        ''' Simulates button click on the remote '''
        self.processor.processEvent(button.id, repeat)
        print "Sleeping for %s before finishing current click ..." % (self.configuration.gapDuration)
        time.sleep(self.configuration.gapDuration)
        print "Done"
    
    def sleelBeforeTest(self):
        time.sleep(self.configuration.gapDuration * self.testDelayFactor)
                
    def testPlusButtonClick(self):
        currentActionList = []
        self.clickButton(self.plusButton, 0)
        currentActionList.append(self.plusButton.click.task)
        self.sleelBeforeTest()
        self.assertEqual(self.processor.executionQueue, currentActionList);
                             
    def testPlusButtonDoubleClick(self):
        currentActionList = []
        self.clickButton(self.plusButton, 0)
        currentActionList.append(self.plusButton.click.task)
        self.clickButton(self.plusButton, 0)
        currentActionList.append(self.plusButton.doubleClick.task)
        self.sleelBeforeTest()
        self.assertEqual(self.processor.executionQueue, currentActionList);        
    
    def testPlusButtonHold(self):
        currentActionList = []
        self.clickButton(self.plusButton, 0)
        currentActionList.append(self.plusButton.click.task)
        self.clickButton(self.plusButton, 1)
        currentActionList.append(self.plusButton.hold.task)
        self.clickButton(self.plusButton, 2)
        currentActionList.append(self.plusButton.hold.task)
        self.sleelBeforeTest()
        self.assertEqual(self.processor.executionQueue, currentActionList);  
            
    def testForwardButtonClick(self):
        currentActionList = []
        self.clickButton(self.forwardButton, 0)
        currentActionList.append(self.forwardButton.click.task)
        self.sleelBeforeTest()
        self.assertEqual(self.processor.executionQueue, currentActionList);
    
    def testForwardButtonDoubleClick(self):
        '''
        Forward button was double-clicked.
        It is only expected that double-click task will be executed and the single-click task should be ignored.
        '''
        currentActionList = []
        self.clickButton(self.forwardButton, 0)        
        self.clickButton(self.forwardButton, 0)
        currentActionList.append(self.forwardButton.doubleClick.task)
        self.sleelBeforeTest()
        self.assertEqual(self.processor.executionQueue, currentActionList, "Should contain only next album task");

    def testForwardButtonHold(self):
        currentActionList = []
        self.clickButton(self.forwardButton, 0)        
        self.clickButton(self.forwardButton, 1)
        currentActionList.append(self.forwardButton.hold.task)
        self.sleelBeforeTest()
        self.assertEqual(self.processor.executionQueue, currentActionList, "Should contain only next playlist task");

    def testMenuButtonClick(self):
        currentActionList = []
        self.clickButton(self.menuButton, 0)
        currentActionList.append(self.menuButton.click.task)
        self.sleelBeforeTest()
        self.assertEqual(self.processor.executionQueue, currentActionList, "Should contain only 1x global menu task");
    
    def testMenuDoubleButtonClick(self):
        currentActionList = []
        self.clickButton(self.menuButton, 0)
        self.clickButton(self.menuButton, 0)
        currentActionList.append(self.menuButton.doubleClick.task)
        self.sleelBeforeTest()
        self.assertEqual(self.processor.executionQueue, currentActionList, "Should contain only 1x global menu task");
        
    def testMenuHold(self):
        currentActionList = []
        self.clickButton(self.menuButton, 0)
        self.clickButton(self.menuButton, 1)
        currentActionList.append(self.menuButton.hold.task)
        self.sleelBeforeTest()
        self.assertEqual(self.processor.executionQueue, currentActionList, "Should contain only 1x current menu task");
        
    def testPlayButtonClick(self):
        currentActionList = []
        self.clickButton(self.playButton, 0)
        currentActionList.append(self.playButton.click.task)
        self.sleelBeforeTest()
        self.assertEqual(self.processor.executionQueue, currentActionList, "Should contain only 1x play-pause task");
    
    def testPlayButtonDoubleClick(self):
        currentActionList = []
        self.clickButton(self.playButton, 0)
        self.clickButton(self.playButton, 0)
        currentActionList.append(self.playButton.click.task)
        self.sleelBeforeTest()
        self.assertEqual(self.processor.executionQueue, currentActionList, "Should contain only 1x play-pause task");
        
    def testPlayButtonHoldx1(self):
        '''
        Play button was hold for 2 rounds.
        Expected no task to be executed as minimal repeats trigger of 5 was not satisfied.
        '''
        currentActionList = []
        self.clickButton(self.playButton, 0)
        self.clickButton(self.playButton, 1)
        self.sleelBeforeTest()
        self.assertEqual(self.processor.executionQueue, currentActionList, "Should be empty");
    
    def testPlayButtonHoldx5(self):
        '''
        Play button was hold for 6 rounds.
        Expected hold task to be executed as minimal repeats trigger is 5 was satisfied.
        '''
        currentActionList = []
        self.clickButton(self.playButton, 0)
        self.clickButton(self.playButton, 1)
        self.clickButton(self.playButton, 2)
        self.clickButton(self.playButton, 3)
        self.clickButton(self.playButton, 4)
        self.clickButton(self.playButton, 5)
        currentActionList.append(self.playButton.hold.task)
        self.sleelBeforeTest()
        self.assertEqual(self.processor.executionQueue, currentActionList, "Should contain only 1x power-off task");
        
if __name__ == "__main__":
    unittest.main()
