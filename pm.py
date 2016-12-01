from pyo import *

class Operator(PyoObject):
    """PM oscillator"""
    def __init__(self, freq=440, pm=None, ratio=1, feedback=0, env=1, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        if pm is not None and not isinstance(pm, PyoObject):
            raise Exception("modulation source must be Pyo object")
        self._freq = freq
        self._ratio = ratio
        self._feedback = feedback
        self._env = env
        self._pm = pm
        self._env = env
        self._pmod = Scale(pm if pm is not None else Sig(0), inmin=-1, inmax=1, outmin=0, outmax=1, mul=env)
        if pm is not None:
            pm.freq = Sig(freq, mul=ratio)
        self._carrier = Sine(freq=self._freq, mul=mul, add=add)
        self._feedback_sig = Scale(self._carrier, inmin=-1, inmax=1, outmin=0, outmax=1, mul=feedback)
        self._carrier.phase = Interp(self._pmod, self._feedback_sig, interp=0.5)
        self._base_objs = self._carrier.getBaseObjects()

    def setFreq(self, freq):
        self._freq = freq
        self._carrier.freq = freq
        if self._pm is not None:
            self._pm.freq = Sig(freq, mul=self._ratio)

    def setPM(self, mod):
        if mod is not None and not isinstance(mod, PyoObject):
            raise Exception("modulation source must be Pyo object")
        self._pm = mod
        if pm is not None:
            mod.freq = Sig(self._freq, mul=self._ratio)
        mod = mod or Sig(0)
        self._pmod.input = mod
        
    def setRatio(self, ratio):
        self._ratio = ratio
        if self._pm is not None:
            self._pm.freq = Sig(self._freq, mul=ratio)

    def setFeedback(self, feedback):
        self._feedback = feedback
        self._feedback_sig.mul = feedback

    def setEnv(self, env):
        self._env = env
        self._pmod.mul = env
        
    @property
    def freq(self):
        return self._freq
    
    @freq.setter
    def freq(self, x):
        self.setFreq(x)
        
    @property
    def pm(self):
        return self._pm

    @pm.setter
    def pm(self, x):
        self.setPM(x)

    @property
    def feedback(self):
        return self._feedback

    @feedback.setter
    def feedback(self, x):
        self.setFeedback(x)

    @property
    def ratio(self):
        return self._ratio

    @ratio.setter
    def ratio(self,x):
        self.setRatio(x)

    @property
    def env(self):
        return self._env

    @env.setter
    def env(self,x):
        self.setEnv(x)

    def play(self, dur=0, delay=0):
        self._carrier.play(dur, delay)
        return PyoObject.play(self, dur, delay)

    def stop(self):
        self._carrier.stop()
        return PyoObject.stop(self)

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._carrier.play(dur, delay)
        return PyoObject.out(self, chnl, inc, dur, delay)

    def sig(self):
        return self._carrier
        
    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [
            SLMapFreq(self._freq),
            SLMap(0, 10, "lin", "ratio", self._ratio),
            SLMap(-1,1, "lin", "feedback", self._feedback),
            SLMapMul(self.mul)
        ]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

        
            
