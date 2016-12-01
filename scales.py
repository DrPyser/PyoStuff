from pyo import *

scales = {
    "minor":[0, 2, 3, 5, 7, 8, 10],
    "chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    "major":[0, 2, 4, 5, 7, 9, 11],
    "blues": [0, 2, 3, 4, 5, 7, 9, 10, 11],
    "diatonic minor": [0, 2, 3, 5, 7, 8, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "harmonic minor": [0, 2, 3, 5, 7, 8, 11],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "turkish": [0, 1, 3, 5, 7, 10, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    "indian": [0, 1, 1, 4, 5, 8, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10]
}

chords = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "seventh": [0, 4, 7, 10],
    "seventh major": [0, 4, 7, 11],
    "minor seventh": [0, 3, 7, 10],
    "minor seventh major": [0, 3, 7, 11]
}

class SemitoneTranspose(PyoObject):
    """
    Transpose an input signal a given number of semitones above or below.

    :Parent: :py:class:`PyoObject`

    :Args:

        input : PyoObject
            Input signal which represents a frequency, in hertz or midi note numbers.
        transpose : float or PyoObject
            Number of semitones above(positif) or below(negatif) the input signal to transpose to.
        scale : int { 0, 1 }
            scale type of the input signal
                0 = midi note number
                1 = frequency in Hertz
    """    
    def __init__(self, input, transpose=1, scale=0):
        PyoObject.__init__(self)
        self._input = input
        self._transpose = transpose
        self._scale = scale        
        input, transpose, scale, lmax = convertArgsToLists(input, transpose, scale)
        self._in_fader = InputFader(input)

        self._transpose_sig = Sig(transpose)
        self._out = Sig(self._in_fader,
                        mul=[Pow(2, Sig(1)/wrap(self._transpose_sig, i)) if wrap(scale, i) == 1 else 1 for i in range(lmax)],
                        add=[wrap(self._transpose_sig, i) if wrap(scale, i) == 0 else 0 for i in range(lmax)])
        self._base_objs = self._out.getBaseObjects()

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

    def setTranspose(self, x):
        """
        Replace the `transpose` attribute.

        :Args:

            x : float or PyoObject
                new transposition value
        """
        self._transpose = x
        self._transpose_sig.setValue(x)        

    def setScale(self, x):
        """
        Replace the `scale` attribute.

        :Args:

            x : int {0,1}
                New scale value
        """
        self._scale = x
        scale, lmax = convertArgsToLists(x)
        self._out.mul = [Pow(2, Sig(1)/wrap(self._transpose_sig, i)) if wrap(scale, i) == 1 else 1 for i in range(lmax)]
        self._out.add = [wrap(self._transpose_sig, i) if wrap(scale, i) == 0 else 0 for i in range(lmax)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [
            SLMap(-12, 12, "lin", "transpose", self._transpose, res="float"),
            SLMap(0, 1, "lin", "scale", self._scale, res="int", dataOnly=True)
        ]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        return self._input
    @input.setter
    def input(self, x):
        self.setInput(x)

    @property
    def transpose(self):
        return self._transpose
    @transpose.setter
    def transpose(self, x):
        self.setTranspose(x)

    @property
    def scale(self):
        return self._scale
    @scale.setter
    def scale(self, x):
        self.setScale(x)
    

class OctaveTranspose(PyoObject):
    """
    Transpose an input signal a given number of octaves above or below.

    :Parent: :py:class:`PyoObject`

    :Args:

        input : PyoObject
            Input signal which represents a frequency, in hertz or midi note numbers.
        transpose : float or PyoObject
            Number of octaves above(positif) or below(negatif) the input signal to transpose to.
        scale : int { 0, 1 }
            scale type of the input signal
                0 = midi note number
                1 = frequency in Hertz
    """    
    def __init__(self, input, transpose=1, scale=0):
        PyoObject.__init__(self)
        self._input = input
        self._transpose = transpose
        self._scale = scale        
        input, transpose, scale, lmax = convertArgsToLists(input, transpose, scale)
        self._in_fader = InputFader(input)

        self._transpose_sig = Sig(transpose)
        self._out = Sig(self._in_fader,
                        mul=[Pow(2, wrap(self._transpose_sig, i)) if wrap(scale, i) == 1 else 1 for i in range(lmax)],
                        add=[wrap(self._transpose_sig, i)*12 if wrap(scale, i) == 0 else 0 for i in range(lmax)])
        self._base_objs = self._out.getBaseObjects()

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

    def setTranspose(self, x):
        """
        Replace the `transpose` attribute.

        :Args:

            x : float or PyoObject
                new transposition value
        """
        self._transpose = x
        self._transpose_sig.setValue(x)        

    def setScale(self, x):
        """
        Replace the `scale` attribute.

        :Args:

            x : int {0,1}
                New scale value
        """
        self._scale = x
        scale, lmax = convertArgsToLists(x)
        self._out.mul = [Pow(2, wrap(self._transpose_sig, i)) if wrap(scale, i) == 1 else 1 for i in range(lmax)]
        self._out.add = [wrap(self._transpose_sig, i)*12 if wrap(scale, i) == 0 else 0 for i in range(lmax)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [
            SLMap(-10, 10, "lin", "transpose", self._transpose, res="float"),
            SLMap(0, 1, "lin", "scale", self._scale, res="int", dataOnly=True)
        ]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        return self._input
    @input.setter
    def input(self, x):
        self.setInput(x)

    @property
    def transpose(self):
        return self._transpose
    @transpose.setter
    def transpose(self, x):
        self.setTranspose(x)

    @property
    def scale(self):
        return self._scale
    @scale.setter
    def scale(self, x):
        self.setScale(x)

class Transpose(PyoObject):
    """
    Transpose a signal in the first octave(midi notes 0 to 11) to a new octave and tonic.

    :Parent: :py:class:`PyoObject`

    :Args:

        input : PyoObject
            Input signal which represents a frequency, in hertz or midi note numbers,
            in the first octave with the tonic 0.
        tonic : float or PyoObject
            midi note number reprenting the frequency of the tonic of the output signal.
        octave : float or PyoObject
            value reprenting the number of the octave to which to transpose the input signal.            
        scale : int { 0, 1 }
            scale type of the input signal
                0 = midi note number
                1 = frequency in Hertz
    """    
    def __init__(self, input, tonic=0, octave=0, scale=0):        
        PyoObject.__init__(self)
        self._input = input
        self._tonic = tonic
        self._octave = octave
        self._scale = scale        
        input, tonic, octave, scale, lmax = convertArgsToLists(input, tonic, octave, scale)
        self._in_fader = InputFader(input)
        self._tonic_sig = Sig(tonic)
        self._octave_sig = Sig(octave)
        self._out = Sig(self._in_fader,
                        mul=[Pow(2, wrap(self._octave_sig, i)/wrap(self._tonic_sig, i))
                             if wrap(scale, i) == 1 else 1 for i in range(lmax)],
                        add=[wrap(self._octave_sig, i)*12 + wrap(self._tonic_sig, i) if wrap(scale, i) == 0 else 0 for i in range(lmax)])
        self._base_objs = self._out.getBaseObjects()

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

    def setTonic(self, x):
        """
        Replace the `tonic` attribute.

        :Args:

            x : float or PyoObject
                new tonic value
        """
        self._tonic = x
        self._tonic_sig.setValue(x)        

    def setOctave(self, x):
        """
        Replace the `octave` attribute.

        :Args:

            x : float or PyoObject
                new octave value
        """
        self._octave = x
        self._octave_sig.setValue(x)        

        
    def setScale(self, x):
        """
        Replace the `scale` attribute.

        :Args:

            x : int {0,1}
                New scale value
        """
        self._scale = x
        scale, lmax = convertArgsToLists(x)
        self._out.mul = [Pow(2, wrap(self._octave_sig, i)/wrap(self._tonic_sig, i)) if wrap(scale, i) == 1 else 1 for i in range(lmax)]
        self._out.add = [wrap(self._octave_sig, i)*12 + wrap(self._tonic_sig, i) if wrap(scale, i) == 0 else 0 for i in range(lmax)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [
            SLMap(0, 10, "lin", "octave", self._octave, res="int"),
            SLMap(0, 12, "lin", "tonic", self._tonic, res="int"),
            SLMap(0, 1, "lin", "scale", self._scale, res="int", dataOnly=True)
        ]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        return self._input
    @input.setter
    def input(self, x):
        self.setInput(x)

    @property
    def tonic(self):
        return self._tonic
    @tonic.setter
    def tonic(self, x):
        self.setTonic(x)

    @property
    def octave(self):
        return self._octave
    @octave.setter
    def octave(self, x):
        self.setOctave(x)
        
    @property
    def scale(self):
        return self._scale
    @scale.setter
    def scale(self, x):
        self.setScale(x)
   

def transpose_scale(scale, octave=0, tonic=0):
    "Transposes a midi scale in the first octave(0-12) to a new octave and tonic"
    return [x+tonic+octave*12 for x in scale]
