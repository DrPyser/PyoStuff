from pyo import *

##TODO: Find formula for Follower Amplitude
##http://www.matthieuamiguet.ch/blog/diy-guitar-effects-python

class Autowah(PyoObject):
    """Auto-wah effect"""
    def __init__(self, input, folfreq=30, minfreq=20, maxfreq=2000, q=5, curve=1, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._curve = curve
        self._folfreq = folfreq
        self._filter_min_freq = minfreq
        self._filter_max_freq = maxfreq
        self._filter_q = q
        self._in_fader = InputFader(input)
        self._follower = Follower(self._in_fader, freq=folfreq)
        self._scaled_follower = Scale(self._follower, inmin=0, inmax=1, outmin=minfreq, outmax=maxfreq, exp=curve)
        self._filter = Biquad(self._in_fader, freq=self._scaled_follower, q=q, type=2)
        self._base_objs = self._filter.getBaseObjects()

    def setFolFreq(self, freq):
        self._folfreq = freq
        self._follower.freq = freq

    def setQ(self, q):
        self._filter_q = q
        self._filter.q = q

    def setMinFreq(self, freq):
        self._filter_min_freq = freq
        self._scaled_follower.outmin = freq

    def setMaxFreq(self, freq):
        self._filter_max_freq = freq
        self._scaled_follower.outmax = freq

    def setInput(self, x, fadetime=0.05):
        """
        Replace the `input` attribute.

        :Args:

            x : PyoObject
                New signal to process.
            fadetime : float, optional
                Crossfade time between old and new input. Defaults to 0.05.
        """
        self._input = x
        self._in_fader.setInput(x, fadetime)

    def setCurve(self, x):
        self._curve = x
        self._scaled_follower.exp = x

    @property
    def curve(self):
        return self._curve
    
    @curve.setter
    def curve(self, x):
        self.setCurve(x)
        
    @property
    def folfreq(self):
        return self._folfreq

    @folfreq.setter
    def folfreq(self, x):
        self.setFolFreq(x)

    @property
    def q(self):
        return self._filter_q

    @q.setter
    def q(self, x):
        self.setQ(x)

    @property
    def minfreq(self):
        return self._filter_min_freq

    @minfreq.setter
    def minfreq(self,x):
        self.setMinFreq(x)

    @property
    def maxfreq(self):
        return self._filter_max_freq

    @maxfreq.setter
    def maxfreq(self,x):
        self.setMaxFreq(x)

    @property # getter
    def input(self):
        """PyoObject. Input signal to process."""
        return self._input
    
    @input.setter # setter
    def input(self, x):
        self.setInput(x)

    def play(self, dur=0, delay=0):
        self._filter.play(dur, delay)
        return PyoObject.play(self, dur, delay)

    def stop(self):
        self._filter.stop()
        return PyoObject.stop(self)

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._filter.play(dur, delay)
        return PyoObject.out(self, chnl, inc, dur, delay)

    def sig(self):
        return self._filter
        
    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [
            SLMap(10, 20000, "log", "folfreq", self.folfreq),
            SLMap(10, 20000, "log", "minfreq", self.minfreq, dataOnly=True),
            SLMap(10, 20000, "log", "maxfreq", self.maxfreq, dataOnly=True),            
            SLMap(1, 500, "log", "q", self.q),
            SLMap(0.01, 10, "log", "curve", self.curve, dataOnly=True),
            SLMapMul(self.mul)
        ]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

        
            
class Autowah2(PyoObject):
    """Auto-wah effect"""
    def __init__(self, input, folfreq=30, minfreq=20, maxfreq=2000, q=5, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._folfreq = folfreq
        self._filter_min_freq = minfreq
        self._filter_max_freq = maxfreq
        self._filter_q = q
        self._in_fader = InputFader(input)
        minfreq, maxfreq, lmax = convertArgsToLists(minfreq, maxfreq)
        self._follower = Follower(self._in_fader, freq=folfreq, mul=[wrap(maxfreq, i)-wrap(minfreq, i) for i in range(lmax)], add=minfreq)
        self._filter = Biquad(self._in_fader, freq=self._follower, q=q, type=2)
        self._base_objs = self._filter.getBaseObjects()

    def setFolFreq(self, freq):
        self._folfreq = freq
        self._follower.freq = freq

    def setQ(self, q):
        self._filter_q = q
        self._filter.q = q

    def setMinFreq(self, freq):
        self._filter_min_freq = freq
        minfreq, maxfreq, lmax = convertArgsToLists(freq, self._filter_max_freq)
        self._follower.add = minfreq
        self._follower.mul = [wrap(maxfreq, i)-wrap(minfreq, i) for i in range(lmax)]

    def setMaxFreq(self, freq):
        self._filter_max_freq = freq
        minfreq, maxfreq, lmax = convertArgsToLists(self._filter_min_freq, freq)
        self._follower.mul = [wrap(maxfreq, i)-wrap(minfreq, i) for i in range(lmax)]

    def setInput(self, x, fadetime=0.05):
        """
        Replace the `input` attribute.

        :Args:

            x : PyoObject
                New signal to process.
            fadetime : float, optional
                Crossfade time between old and new input. Defaults to 0.05.
        """
        self._input = x
        self._in_fader.setInput(x, fadetime)
        
    @property
    def folfreq(self):
        return self._folfreq

    @folfreq.setter
    def folfreq(self, x):
        self.setFolFreq(x)

    @property
    def q(self):
        return self._filter_q

    @q.setter
    def q(self, x):
        self.setQ(x)

    @property
    def minfreq(self):
        return self._filter_min_freq

    @minfreq.setter
    def minfreq(self,x):
        self.setMinFreq(x)

    @property
    def maxfreq(self):
        return self._filter_max_freq

    @maxfreq.setter
    def maxfreq(self,x):
        self.setMaxFreq(x)

    @property # getter
    def input(self):
        """PyoObject. Input signal to process."""
        return self._input
    @input.setter # setter
    def input(self, x):
        self.setInput(x)

    def play(self, dur=0, delay=0):
        self._filter.play(dur, delay)
        return PyoObject.play(self, dur, delay)

    def stop(self):
        self._filter.stop()
        return PyoObject.stop(self)

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._filter.play(dur, delay)
        return PyoObject.out(self, chnl, inc, dur, delay)

    def sig(self):
        return self._filter
        
    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [
            SLMap(10, 20000, "log", "folfreq", self.folfreq),
            SLMap(10, 20000, "log", "minfreq", self.minfreq, dataOnly=True),
            SLMap(10, 20000, "log", "maxfreq", self.maxfreq, dataOnly=True),            
            SLMap(1, 500, "log", "q", self.q),
            SLMapMul(self.mul)
        ]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

        
            
