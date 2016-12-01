from pyo import *
from itertools import *
from triggers import *

class MidiEnv(PyoObject):
    def __init__(self, input, adtable, reltable, addur=.5, reldur=.5, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._adtable = adtable
        self._reltable = reltable
        self._addur = addur
        self._reldur = reldur
        self._in_fader = InputFader(input)
        self._trigon = Thresh(self._in_fader, threshold=0.0, dir=0)
        self._trigoff = Select(self._in_fader, value=0)
        adtable, reltable, lmax = convertArgsToLists(adtable, reltable)
        self._sustain = Sig([wrap(adtable, i).getPoints()[-1][1] for i in range(lmax)])
        self._adenv = TrigEnv(self._trigon, adtable, dur=addur)
        self._susenv = TrigMap((self._adenv["trig"], self._trigoff), values=(self._sustain, 0), init=0)
        self._relenv = TrigEnv(self._trigoff, reltable, dur=reldur, mul=SampHold(self._adenv+self._susenv, self._trigoff, value=1))
        self._phase = TrigMap((self._trigon, self._adenv["trig"], self._trigoff), values=(0, 1, 2), init=0)
        self._mix = Selector([self._adenv, self._susenv, self._relenv], voice=self._phase, mul=Sig(self._in_fader, mul=self._mul))
        self._base_objs = self._mix.getBaseObjects()

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        return self.play(dur, delay)

    def setInput(self, x, fadetime=0.05):
        """
        Replace the `inputs` attribute.

        :Args:

            x : PyoObject
                New signal used to trigger the envelope.
            fadetime : float, optional
                Crossfade time between old and new input. Defaults to 0.05.

        """
        pyoArgsAssert(self, "oN", x, fadetime)
        self._input = x
        self._in_fader.setInput(x, fadetime)

    def setAttackDecayDur(self, x):
        """
        Replace the `addur` attribute,
        which controls the duration of the attack-decay phase
        of the envelope

        :Args:

            x : float
                new `addur` attribute.

        """
        pyoArgsAssert(self, "n", x)
        self._addur = x
        self._adenv.dur = x

    def setReleaseDur(self, x):
        """
        Replace the `reldur` attribute,
        which controls the duration of the release phase
        of the envelope.

        :Args:

            x : float
                new `reldur` attribute.

        """
        pyoArgsAssert(self, "n", x)
        self._reldur = x
        self._relenv.dur = x

    def setADTable(self, x):
        """
        Replace the `table` attribute,
        which controls the table which describes
        the form of the envelope.

        :Args:

            x : PyoTableObject
                new `table` attribute. 

        """
        self._adtable = x
        self._adenv.table = x

    def setSustain(self, x):
        """
        Replace the `sustain` attribute,
        changing the value of the point given by the `sustainpoint`
        attribute.

        :Args:

            x : float
                value of the new sustain

        """
        self._adtable.list[-1][1] = x
        
    @property
    def sustain(self):
        """float. Amplitude of the sustain phase, as fraction of the peak amplitude."""
        return self._sustain
    
    @sustain.setter
    def sustain(self, x): self.setSustain(x)

    @property
    def addur(self):
        return self._addur

    @addur.setter
    def addur(self, x):
        self.setAttackDecayDur(x)

    @property
    def reldur(self):
        return self._reldur

    @reldur.setter
    def reldur(self, x):
        self.setReleaseDur(x)
