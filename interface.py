#!/usr/bin/python

import Tkinter
import pymedia.audio.sound as sound
from Sound import *
from Filter import *

inputSound = loadSoundFromFile('static.wav')

zeroList = []
zeroList.append(-0.25 + 0j)
zeroList.append(0.5 + 0j)

poleList = []
poleList.append(-0.5j)
poleList.append(0.5j)

testFilter = Filter(zeroList, poleList)
filteredSamples = testFilter.filterStream(inputSound.sampleFloats)

inputSound.sampleFloats = filteredSamples
saveSoundToFile(inputSound, 'out.wav')

format = sound.AFMT_S16_LE
snd = sound.Output(inputSound.sampleRate, inputSound.channelCount, format)
snd.play(getWaveBytes(inputSound))

normalizedSoundFloats = filteredSamples

top = Tkinter.Tk()

'''
Proposed Design:
 -use non-linear radius expansion for z-plane graph (radius squared?)
 -graph s-plane from x of -c to c so that z-plane has radius from exp(-c) to exp(c)
 -graph frequency response by finding magnitude of various points in z- or s- plane
 -have ability to add single real point or a conjugate pair
 -restrict poles to within unit circle for z-plane and negative half for s-plane
 -add buttons to play original audio and new, filtered audio
 -maybe use file dialog boxes for loading/saving WAV files?
 -maybe use sliding window for graphing of audio wave forms?
 -maybe have ability to generate sounds (statics, waves, drum beats)?
'''

canvas = Tkinter.Canvas(top, bg="white", width=512, height=512)
button = Tkinter.Button(top, text="button")

canvas.create_line(0.0, 256.0, 512.0, 256.0)
widthCompressionFactor = 512.0 / len(normalizedSoundFloats)

for sampleIndex in range(1, len(normalizedSoundFloats)):
    xA = (sampleIndex - 1) * widthCompressionFactor
    yA = 256.0 - 128.0 * normalizedSoundFloats[sampleIndex - 1]
    xB = sampleIndex * widthCompressionFactor
    yB = 256.0 - 128.0 * normalizedSoundFloats[sampleIndex]
    canvas.create_line(xA, yA, xB, yB)

canvas.pack()
button.pack()

top.mainloop()
