'''
Created on 8 Mar 2012

@author: adambednarski
'''

import alsaaudio

class MixerDevice():
    '''
    MixerDevice
    '''

    def __init__(self, name = "Master", idx=0):
        self.mixerDevice = alsaaudio.Mixer(name, cardindex=idx)

    
    