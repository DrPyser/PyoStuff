from pyo import *
from itertools import *

def wrap_around(iterable, length):
    iterable = tuple(iterable)
    for i in range(length):
        yield wrap(iterable, i)

class TrigMap(PyoObject):
    """
    Output a given value when a trigon

    Map each input trigger to a corresponding value(with wrap around).    
    When a trigger is received, the corresponding value is outputted.

    :Parent: :py:class:`PyoObject`

    :Args:

        inputs : list of PyoObject
            Audio signals sending triggers.
        values : float or PyoObject, optional
            Corresponding values for each trigger in `inputs`. Defaults to 0.
        init : float, optional
            Initial value. Defaults to 0.

    .. note::

        The out() method is bypassed. TrigVal's signal can not be sent
        to audio outs.

    """
    def __init__(self, inputs, values=0., init=0., mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._inputs = inputs
        self._values = values
        inputs, values, init, lmax = convertArgsToLists(inputs, values, init)
        for i in range(max([len (inputs), len (values)])):
            if len(wrap(values, i)) > len(wrap(inputs, i)):
                print "Warning: length of values tuple(" + str(wrap(values, i)) + ") greater than length of associated input triggers tuple."

        self._val = Sig(list(wrap_around(init, len(inputs))), mul=mul, add=add)
        self._trigfuncs = [TrigFunc(list(wrap(inputs, i)),
                                    function=lambda x: wrap(self._val, i).setValue(x),
                                    arg=list(wrap(values, i)))
                           for i in range(lmax)
        ]
                           
        self._base_objs = self._val.getBaseObjects()

    def setInputs(self, x):
        """
        Replace the `input` attribute.

        :Args:

            x : PyoObject
                New signal to process.
            fadetime : float, optional
                Crossfade time between old and new input. Defaults to 0.05.

        """
        self._inputs = x
        self._val.value = self._val.value + list(wrap_around)
        inputs, values, init, lmax = convertArgsToLists(x, self._values, init)
        self._val.value = self._val.value + list(wrap_around(init, len(inputs) - len(self._val)))
        for i in range(len(inputs)):
            if i < len(self._trigfuncs):
                self._trigfuncs[i].setInput(list(inputs[i]))
            else:
                self._trigfuncs.append(TrigFunc(list(wrap(inputs, i)),
                                                function=lambda x: wrap(self._val, i).setValue(x),
                                                arg=list(wrap(values, i))))

    def setValues(self, x):
        """
        Replace the `value` attribute.

        :Args:

            x : float or PyoObject
                new `value` attribute.

        """
        
        self._values = x
        values, inputs, lmax = convertArgsToLists(x, self._inputs)
        for i in range(len(values)):
            if len(wrap(values, i)) > len(wrap(inputs, i)):
                print "Warning: length of values tuple greater than length of input triggers tuple."
            if i < len(self._trigfuncs):
                self._trigfuncs[i].setArg(list(values[i]))
            else:
                self._trigfuncs.append(TrigFunc(list(wrap(inputs, i)),
                                                function=lambda x: wrap(self._val, i).setValue(x),
                                                arg=list(wrap(values, i))))

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        return self.play(dur, delay)

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def inputs(self):
        """PyoObject. Audio trigger signal."""
        return self._inputs
    @inputs.setter
    def inputs(self, x):
        self.setInputs(x)
    @property
    def values(self):
        """float or PyoObject. Next value."""
        return self._values
    @values.setter
    def values(self, x):
        self.setValues(x)

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
