
'''
Created on 6 Mar 2012

@author: abednarski
'''
from main.controller.volume.mixer_facade import MixerFacade

class VolumeController:

    def __init__(self, volume = 100, mixer = None):
        if(mixer is None):     
            self.mixer = MixerFacade(None)
        else:
            self.mixer = mixer        
        
    def volumeUp(self, step=1):
        print "Volume up: %s" % (step)
        volume = self.mixer.getVolume() + step
        self.mixer.setVolume(volume)
        
    def volumeDown(self, step=-1):
        print "Volume down: %s" % (step)
        volume = self.mixer.getVolume() + step
        self.mixer.setVolume(volume)        
        
    def mute(self):
        print "Mute"
        self.mixer.mute()
        
    def unMute(self):
        print "Unmute"
        self.mixer.unMute()
    
    def getVolume(self):
        self.mixer.getVolume()
         
    def getMute(self):
        self.mixer.getMute()