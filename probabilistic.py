from __future__ import print_function

from pyo import *

import numpy.random as np

def ff():
    global value
    srt = sorted(prob)
    tot = sum([x[1] for x in srt])
    maxi = srt[-1][0] + 1
    accum = 0
    rnd = random.randint(0, tot)
    for i in range(len(srt)):
        accum += srt[i][1]
        if accum > rnd:
            value = srt[i][0]
            break
    print(value)

class TrigProb(PyoObject):
    def __init__(self, input, choices, probabilities, mul=1, add=0):        
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._choices = choices
        self._probabilities = probabilities
        self._in_fader = InputFader(input)
        choices, probabilities, lmax = convertArgsToLists(choices, probabilities)
        for p in probabilities:
            assert sum(p) == 1, "Sum of probabilities not equal to 1.0"
            
        self._chooser = TrigFunc(self._in_fader, function=lambda (c, p):self._value.setValue(float(np.choice(c, p=p))),
                                 arg=zip(choices, probabilities))
        self._value = Sig(0)
        self._base_objs = self._value.getBaseObjects()

    def setInput(self, input, fadetime=0.05):
        self._input = input
        self._in_fader.setInput(input, fadetime)

    def setChoices(self, choices):
        self._choices = choices
        choices, probabilities, lmax = convertArgsToLists(choices, self._probabilities)
        self._chooser.arg = zip(choices, probabilities)

    def setProbabilities(self, probabilities):
        self._probabilities = probabilities
        choices, probabilities, lmax = convertArgsToLists(self._choices, probabilities)
        self._chooser.arg = zip(choices, probabilities)

    @property
    def input(self):
        return self._input
    @input.setter
    def input(self, x):
        self.setInput(x)

    @property
    def choices(self):
        return self._choices
    @choices.setter
    def choices(self, x):
        self.setChoices(x)

    @property
    def probabilities(self):
        return self._probabilities
    @probabilities.setter
    def probabilities(self, x):
        self.setProbabilities(x)

        

if __name__ == '__main__':
    s = Server().boot()
    s.amp = 0.1
    s.verbosity = 0
    m = Metro(time=1).play()
    a = TrigProb(m, choice=(35,36,45,46, 56), probabilities=(.1,.2,.3,.2,.2))
    b = SineLoop(freq=MToF(a), feedback=.25)
    mix = b.mix(2).out()
    s.gui(locals())
