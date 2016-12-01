#!/usr/bin/env python
# encoding: utf-8
from pyo import *

class Pulse(Pulsar):
    """ Pulse waveforms, with variable pulse width(duty) and multiple possible waveforms.

    :Parent: :py:class:`PyoObject`

    :Args:

        freq : float or PyoObject, optional
            Oscillator frequency in cycles per second. The frequency is
            internally clamped between 0.00001 and sr/4. Defaults to 100.
        phase : float or PyoObject, optional
            Phase of sampling, expressed as a fraction of a cycle (0 to 1).
            Defaults to 0.
        duty : float or PyoObject, optional
            duty cycle of the pulse, i.e. pulse width(fraction of the period which is spent on the waveform), expressed as a fraction of a cycle (0 to 1).
            Defaults to 0.5.

        type : int, optional
            Waveform type. five possible values :
            0: pulse
            1: triangle
            2: saw up
            3: saw down
            4: sine
    .. seealso::

        :py:class:`Pulsar`, :py:class:`PWM`
    """
    
    def __init__(self, freq=440, phase=0, duty=0.5, type=0, mul=1,add=0):
        self._duty = duty
        self._type = type
        self._types = {
            0: lambda:  LinTable([(0,1),(8192,1)]),
            1: lambda:  LinTable([(0,0), (4096, 1), (8192,0)]),
            2: lambda:  LinTable([(0,0),(8192,1)]),
            3: lambda:  LinTable([(0,1),(8192,0)]),
            4: lambda:  CosTable([(0,0), (4096, 1), (8192,0)])
        }

        type, lmax = convertArgsToLists(type)
        Pulsar.__init__(self, table=[self._types[wrap(type, i)]() for i in range(lmax)],
                        env=LinTable([(0,1),(8192,1)]), freq=freq, phase=phase, frac=self._duty,mul=mul,add=add)

    def setType(self, type):
        self._type= type
        type, lmax = convertArgsToLists(type)
        self.setTable([self._types[wrap(type, i)]() for i in range(lmax)])

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, x):
        self.setType(x)
        
    @property
    def duty(self):
        """float or PyoObject. Duty cycle of the pulse waveform(pulse width)."""
        return self._frac
    @duty.setter
    def duty(self, x):
        self.setFrac(x)

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMapFreq(self._freq),
                          SLMap(0.01,1,"log","duty", self._duty),
                          SLMap(0, 4, "lin", "type", self._type, res="int", dataOnly=True),
                          SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)
        



class PWM(Pulse):
    """Pulse-Width Modulation Signal Generator
    
    :Parent: :py:class:`Pulse`

    :Args:

        ratio : float or PyoObject, optional
            A factor that, when multiplied by the `freq` parameter,
            gives the modulator frequency. Defaults to 1.
        index : float or PyoObject, optional
            The modulation index. This value multiplied by 0.5 
            gives the modulator amplitude(the modulator amplitude will vary between 0 and 1). 
            Defaults to 1.
    """

    def __init__(self, freq=440, type=0, ratio=1, index=1, mul=1, add=0):
        self._ratio = ratio
        self._index = index
        freq, ratio, index, lmax = convertArgsToLists(freq, ratio, index)
        self._mod = Sine(freq=Sig(freq, mul=ratio),
                         mul=Sig(0.5, mul=index), add=.5)
        Pulse.__init__(self, freq=freq, type=type, duty=self._mod, mul=mul, add=add)


    def setRatio(self, ratio):
        """
        Replace the `ratio` attribute.

        :Args:

            x : float or PyoObject
                new `ratio` attribute.

        """

        self._ratio = ratio
        freq, ratio, lmax = convertArgsToLists(self._freq, ratio)
        self._mod.freq = [Sig(wrap(ratio, i))*wrap(freq, i) for i in range(lmax)]

    def setIndex(self, index):
        """
        Replace the `index` attribute.

        :Args:

            x : float or PyoObject
                new `index` attribute.

        """
        self._index = index
        index, lmax = convertArgsToLists(index)
        self._mod.mul = [Sig(wrap(index, i))*0.5 for i in range(lmax)]

    def setFreq(self, freq):
        """
        Replace the `freq` attribute.

        :Args:

            x : float or PyoObject
                new `freq` attribute.

        """
        self._freq = freq
        freq, ratio, index, lmax = convertArgsToLists(freq, self._ratio, self._index)
        self._mod.freq = [Sig(wrap(freq, i))*wrap(ratio, i) for i in range(lmax)]

    @property
    def ratio(self):
        """float or PyoObject. Modulator/Carrier ratio."""
        return self._ratio

    @ratio.setter
    def ratio(self, x):
        self.setRatio(x)

    @property
    def index(self):
        """float or PyoObject. modulation index."""
        return self._index

    @index.setter
    def index(self, x):
        self.setIndex(x)

    @property
    def freq(self):
        """float or PyoObject. Carrier frequency."""
        return self._freq

    @freq.setter
    def freq(self,x):
        self.setFreq(x)
    
    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(10, 2000, "log", "freq", self._freq),
                          SLMap(0, 4, "lin", "type", self._type, res="int", dataOnly=True),
                          SLMap(0.01, 10, "log", "ratio", self._ratio),
                          SLMap(0.01, 10, "log", "index", self._index),
                          SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)


