from pyo import *

class Flanger(PyoObject):
    """Flanger effect"""
    def __init__(self, input, freq=1, maxdelay=.005, feedback=0, depth=.5, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._depth = depth
        self._freq = freq
        self._maxdelay = maxdelay
        self._feedback = feedback
        self._in_fader = InputFader(input)

        in_fader, depth, maxdelay, freq, feedback, mul, add, lmax = convertArgsToLists(self._in_fader, depth, maxdelay, freq, feedback, mul, add)

        self._modamp = Sig(depth, mul=maxdelay)
        self._lfo = Sine(freq=freq, mul=self._modamp, add=maxdelay)
        self._delay = Delay(input, delay=self._lfo, feedback=feedback)        
        self._flange = Interp(in_fader, self._delay, mul=mul, add=add)
        self._base_objs = self._flange.getBaseObjects()

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

    def setDepth(self, x):
        """
        Replace the `depth` attribute.

        :Args:

            x : float or PyoObject
                New `depth` attribute.

        """
        self._depth = x
        self._modamp.value = x

    def setFreq(self, x):
        """
        Replace the `freq` attribute.

        :Args:

            x : float or PyoObject
                New `freq` attribute.

        """
        self._freq = x
        self._lfo.freq = x

    def setFeedback(self, x):
        """
        Replace the `feedback` attribute.

        :Args:

            x : float or PyoObject
                New `feedback` attribute.

        """
        self._feedback = x
        self._delay.feedback = x

    @property
    def input(self):
        """PyoObject. Input signal to process."""
        return self._input
    @input.setter
    def input(self, x):
        self.setInput(x)

    @property
    def depth(self):
        """float or PyoObject. Amplitude of the delay line modulation."""
        return self._depth
    @depth.setter
    def depth(self, x):
        self.setDepth(x)

    @property
    def freq(self):
        """float or PyoObject. Frequency of the delay line modulation."""
        return self._freq
    @freq.setter
    def freq(self, x):
        self.setFreq(x)

    @property
    def feedback(self):
        """float or PyoObject. Amount of out sig sent back in delay line."""
        return self._feedback
    @feedback.setter
    def feedback(self, x):
        self.setFeedback(x)


    def play(self, dur=0, delay=0):
        self._flange.play(dur, delay)
        return PyoObject.play(self, dur, delay)

    def stop(self):
        self._flange.stop()
        return PyoObject.stop(self)

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._flange.play(dur, delay)
        return PyoObject.out(self, chnl, inc, dur, delay)

    def sig(self):
        return self._flange

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0., 1., "lin", "depth", self._depth),
                          SLMap(0.001, 20., "log", "freq", self._freq),
                          SLMap(0., 1., "lin", "feedback", self._feedback),
                          SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)
