'''
Created on 6 Mar 2012

@author: abednarski
'''

class MixerFacade():
    
    # , name = "Master", idx=0
    # self.mixerDevice = alsaaudio.Mixer(name, cardindex=idx)
    def __init__(self, mixerDevice):
        self.mixerDevice = mixerDevice
        
    def setVolume(self, volume):        
        self.mixerDevice.setvolume(volume)
        
    def getVolume(self):
        return self.mixerDevice.getvolume()
        
    def mute(self):
        self.mixerDevice.setmute(1)
        
    def unMute(self):
        self.mixerDevice.setmute(0)        
        
    def getMute(self):
        self.mixerDevice.getmute()
                