# PyoStuff
Stuff written with Pyo Python dsp library.

* autowah.py : Autowah effect unit;
* flanger.py : Flanger effect unit using delay;
* pwm.py : Pulse waveforms generator using Pulsar, Pulse Wave Modulation generator(Pulse wave with duty modulated at a ratio of oscillator frequency);
* ringmod.py : Ring Modulation effect unit;
* scales.py : scale and chords dictionary(all in the first midi octave), and abstractions for octave and pitch(tonic) transposition, in the form of effect units;
* pm.py : flexible abstraction for phase modulation synthesis with multiple modulators(inspired by DX7);
* modmatrix.py : abstraction for managing a set of interconnected objects in a dsp chain. Think small database for pyo objects, with reversible connections(old value stored and restored on disconnect) and support for queries on current connections and objects.
* midienv.py : attempt at a table-defined midi envelope, with a table for Attack/Decay phase and another for Release. Work In Progress;
* triggers.py : miscellaneous trigger generators or trigger listeners. 
  * Trigmap : given a list(tuple) of triggers and a list(tuple) of numerical values, associate each trigger to a value, such that the output is set to the value associated with the last received trigger. 

