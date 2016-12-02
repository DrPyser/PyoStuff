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

class TrigAnd(PyoObject):
    def __init__(self, trig1, trig2, windowlen=0, mul=1, add=0):
        pyoArgsAssert(self, "ooOOO", trig1, trig2, windowlen, mul, add)
        PyoObject.__init__(self, mul, add)
        self._trig1 = trig1
        self._trig2 = trig2
        self._in_fader1 = InputFader(trig1)
        self._in_fader2 = InputFader(trig2)
        self._windowlen = windowlen
        trig1, trig2, windowlen, lmax = convertArgsToLists(trig1, trig2, windowlen)
        self._hold1 = TrigEnv(self._in_fader1, LinTable([(0,1), (8192,1)]), dur=windowlen)
        self._hold2 = TrigEnv(self._in_fader2, LinTable([(0,1), (8192,1)]), dur=windowlen)
        self._out = Thresh(self._hold1+self._hold2, threshold=1, dir=0)
        self._base_objs = self._out.getBaseObjects()

    def setTrig1(self, x, fadetime=0.05):
        """
        Replace the `trig1` attribute.

        :Args:

            x: PyoObject
                New signal to process.
            fadetime: float, optional
                Crossfade time between old and new input. Default to 0.05.

        """
        pyoArgsAssert(self, "oN", x, fadetime)
        self._trig1 = x
        self._in_fader1.setInput(x, fadetime)


    def setTrig2(self, x, fadetime=0.05):
        """
        Replace the `trig2` attribute.

        :Args:

            x: PyoObject
                New signal to process.
            fadetime: float, optional
                Crossfade time between old and new input. Default to 0.05.

        """
        pyoArgsAssert(self, "oN", x, fadetime)
        self._trig2 = x
        self._in_fader2.setInput(x, fadetime)

    def setWindowlen(self, x):
        self._windowlen = x
        self._timer.time = x

    @property
    def trig1(self):
        """PyoObject. Timer stop signal."""
        return self._trig1
    @trig1.setter
    def trig1(self, x): self.setTrig1(x)

    @property
    def trig2(self):
        """PyoObject. Timer start signal."""
        return self._trig2
    @trig2.setter
    def trig2(self, x): self.setTrig2(x)
    
    @property
    def windowlen(self):
        return self._windowlen
    @windowlen.setter
    def windowlen(self, x):
        self.setWindowlen(x)

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [
            SLMap(0.0001, 10, "log", "windowlen", self._windowlen),
        ]

        PyoObject.ctrl(self, map_list, title, wxnoserver)


class TrigOr(PyoObject):
    def __init__(self, trig1, trig2, windowlen=0, mul=1, add=0):
        pyoArgsAssert(self, "ooOOO", trig1, trig2, windowlen, mul, add)
        PyoObject.__init__(self, mul, add)
        self._trig1 = trig1
        self._trig2 = trig2
        self._in_fader1 = InputFader(trig1)
        self._in_fader2 = InputFader(trig2)
        self._windowlen = windowlen
        trig1, trig2, windowlen, lmax = convertArgsToLists(trig1, trig2, windowlen)
        self._hold1 = TrigEnv(self._in_fader1, LinTable([(0,1), (8192,1)]), dur=windowlen)
        self._hold2 = TrigEnv(self._in_fader2, LinTable([(0,1), (8192,1)]), dur=windowlen)
        self._out = Thresh(self._hold1+self._hold2, threshold=0, dir=0)
        self._base_objs = self._out.getBaseObjects()

    def setTrig1(self, x, fadetime=0.05):
        """
        Replace the `trig1` attribute.

        :Args:

            x: PyoObject
                New signal to process.
            fadetime: float, optional
                Crossfade time between old and new input. Default to 0.05.

        """
        pyoArgsAssert(self, "oN", x, fadetime)
        self._trig1 = x
        self._in_fader1.setInput(x, fadetime)


    def setTrig2(self, x, fadetime=0.05):
        """
        Replace the `trig2` attribute.

        :Args:

            x: PyoObject
                New signal to process.
            fadetime: float, optional
                Crossfade time between old and new input. Default to 0.05.

        """
        pyoArgsAssert(self, "oN", x, fadetime)
        self._trig2 = x
        self._in_fader2.setInput(x, fadetime)

    def setWindowlen(self, x):
        self._windowlen = x
        self._timer.time = x

    @property
    def trig1(self):
        """PyoObject. Timer stop signal."""
        return self._trig1
    @trig1.setter
    def trig1(self, x): self.setTrig1(x)

    @property
    def trig2(self):
        """PyoObject. Timer start signal."""
        return self._trig2
    @trig2.setter
    def trig2(self, x): self.setTrig2(x)
    
    @property
    def windowlen(self):
        return self._windowlen
    @windowlen.setter
    def windowlen(self, x):
        self.setWindowlen(x)

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [
            SLMap(0.0001, 10, "log", "windowlen", self._windowlen),
        ]

        PyoObject.ctrl(self, map_list, title, wxnoserver)

class TrigXor(PyoObject):
    def __init__(self, trig1, trig2, windowlen=0, mul=1, add=0):
        pyoArgsAssert(self, "ooOOO", trig1, trig2, windowlen, mul, add)
        PyoObject.__init__(self, mul, add)
        self._trig1 = trig1
        self._trig2 = trig2
        self._in_fader1 = InputFader(trig1)
        self._in_fader2 = InputFader(trig2)
        self._windowlen = windowlen
        trig1, trig2, windowlen, lmax = convertArgsToLists(trig1, trig2, windowlen)
        self._hold1 = TrigEnv(self._in_fader1, LinTable([(0,1), (8192,1)]), dur=windowlen)
        self._hold2 = TrigEnv(self._in_fader2, LinTable([(0,1), (8192,1)]), dur=windowlen)
        self._out = Select(self._hold1+self._hold2, value=1)
        self._base_objs = self._out.getBaseObjects()

    def setTrig1(self, x, fadetime=0.05):
        """
        Replace the `trig1` attribute.

        :Args:

            x: PyoObject
                New signal to process.
            fadetime: float, optional
                Crossfade time between old and new input. Default to 0.05.

        """
        pyoArgsAssert(self, "oN", x, fadetime)
        self._trig1 = x
        self._in_fader1.setInput(x, fadetime)


    def setTrig2(self, x, fadetime=0.05):
        """
        Replace the `trig2` attribute.

        :Args:

            x: PyoObject
                New signal to process.
            fadetime: float, optional
                Crossfade time between old and new input. Default to 0.05.

        """
        pyoArgsAssert(self, "oN", x, fadetime)
        self._trig2 = x
        self._in_fader2.setInput(x, fadetime)

    def setWindowlen(self, x):
        self._windowlen = x
        self._timer.time = x

    @property
    def trig1(self):
        """PyoObject. Timer stop signal."""
        return self._trig1
    @trig1.setter
    def trig1(self, x): self.setTrig1(x)

    @property
    def trig2(self):
        """PyoObject. Timer start signal."""
        return self._trig2
    @trig2.setter
    def trig2(self, x): self.setTrig2(x)
    
    @property
    def windowlen(self):
        return self._windowlen
    @windowlen.setter
    def windowlen(self, x):
        self.setWindowlen(x)

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [
            SLMap(0.0001, 10, "log", "windowlen", self._windowlen),
        ]

        PyoObject.ctrl(self, map_list, title, wxnoserver)

        
class TrigGate(PyoObject):
    def __init__(self, input, open, close, mul=1, add=0):
        pyoArgsAssert(self, "oooOO", input, open, close, mul, add)
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._open = open
        self._close = close
        self._input_fader = InputFader(input)
        self._open_fader = InputFader(open)
        self._close_fader = InputFader(close)
        self._out = Sig(self._input_fader, mul=TrigMap((self._open_fader, self._close_fader), values=(1, 0)))
        self._base_objs = self._out.getBaseObjects()

    def setInput(self, x, fadetime=0.05):
        """
        Replace the `input` attribute.

        :Args:

            x: PyoObject
                New signal to process.
            fadetime: float, optional
                Crossfade time between old and new input. Default to 0.05.

        """
        pyoArgsAssert(self, "oN", x, fadetime)
        self._input = x
        self._input_fader.setInput(x, fadetime)


    def setOpen(self, x, fadetime=0.05):
        """
        Replace the `open` attribute.

        :Args:

            x: PyoObject
                New signal to process.
            fadetime: float, optional
                Crossfade time between old and new input. Default to 0.05.

        """
        pyoArgsAssert(self, "oN", x, fadetime)
        self._open = x
        self._open_fader.setInput(x, fadetime)

    def setClose(self, x, fadetime=0.05):
        """
        Replace the `close` attribute.

        :Args:

            x: PyoObject
                New signal to process.
            fadetime: float, optional
                Crossfade time between old and new input. Default to 0.05.

        """
        pyoArgsAssert(self, "oN", x, fadetime)
        self._close = x
        self._close_fader.setInput(x, fadetime)

    @property
    def input(self):
        """PyoObject. input signal to pass or block."""
        return self._input
    @input.setter
    def input(self, x): self.setInput(x)

    @property
    def open(self):
        """PyoObject. Timer start signal."""
        return self._open
    @open.setter
    def open(self, x): self.setOpen(x)
    
    @property
    def close(self):
        return self._close
    @close.setter
    def close(self, x):
        self.setClose(x)

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [
            SLMapMul(self._mul)
        ]

        PyoObject.ctrl(self, map_list, title, wxnoserver)
    

if __name__ == '__main__':
    # Running as a script
    s = Server().boot()
    a = Sine()
    b = Trig()
    c = Metro(time=1)
    d = TrigGate(a,b,c)
    Scope(d)
    s.gui(locals())
        
        
