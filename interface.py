#!/usr/bin/python

import Tkinter, tkFileDialog
import cmath
import pymedia.audio.sound as sound

from Sound import *
from Filter import *
from ComplexRoot import *
from Drawable import *

inputSound = loadSoundFromFile('static.wav')

zeroList = []
zeroList.append(-0.5)

poleList = []
poleList.append(0.5)

testFilter = Filter(zeroList, poleList)
filteredSamples = testFilter.filterStream(inputSound.sampleFloats)

originalSamples = inputSound.sampleFloats
inputSound.sampleFloats = filteredSamples
#saveSoundToFile(inputSound, 'out.wav')

format = sound.AFMT_S16_LE
snd = sound.Output(inputSound.sampleRate, inputSound.channelCount, format)
#snd.play(getWaveBytes(inputSound))

#normalizedSoundFloats = filteredSamples

top = Tkinter.Tk()

'''
Proposed Design:
 -(DECLINED) use non-linear radius expansion for z-plane graph (radius squared?)
 -(DECLINED) graph s-plane from x of -c to c so that z-plane has radius from exp(-c) to exp(c)
 -graph frequency response by finding magnitude of various points in z- or s- plane
   -use cubic or cosine interpolation, include pole/zero angles in the sample points
 -(DONE: toggle via button) have ability to add single real point or a conjugate pair
 -(DONE) restrict poles to within unit circle for z-plane and negative half for s-plane
 -(in progress) add buttons to play original audio and new, filtered audio
 -(in progress) maybe use file dialog boxes for loading/saving WAV files?
 -maybe use sliding window for graphing of audio wave forms?
 -maybe have ability to generate sounds (statics, waves, drum beats)?
 -(in progress) maybe an 'apply filter' button?
 -should sound info be its own class and the float array be separate?
'''

'''
Status:
 -core functionality almost entirely done
 -entry list GUI should be fully functional
 -"Build and Play" button constructs filter, filters static sound, and plays
 -"load sound" button works (at least for 16-bit mono WAV files)
 -still need button to play original sound
 -still need button to save filtered sound
'''

'''
Issues:
 -better organization of Drawable class heirarchy? Is heirarchy needed?
 -when zero placed around 1 and pole pair placed around +/-i, sounds like clipping
 -lots of renaming and reorganizing (likely with more modules)
 -will want to make functions that work on a given entry rather than just the active one
'''

'''
GUI ideas:
 -add/remove/modify subroutines operate on list of "entries" in dictionary
   -will be used to update canvases and zero/pole list frame
 -click entry in zero/pole list frame to select as active
 -removing zero/pole can make activeEntry invalid (None as invalid code)
 -group zeros and poles together, have different modifying subroutines
 -group single reals and conjugate pairs together also (different subroutines)
 -to move a single real in the s-plane from 0j to +/-pij, use half-spaces
   -boundaries determined at +/-pij/2, click beyond to alternate 0 and pi phases
   -actually, appears to be emergent behavior from graphing corrected positions!
'''

canvasWidth = 400
canvasHeight = 400

zPlane = Tkinter.Canvas(top, bg="white", width=canvasWidth, height=canvasHeight)
sPlane = Tkinter.Canvas(top, bg="white", width=canvasWidth, height=canvasHeight)
topFrame = Tkinter.Frame(top)
frame = Tkinter.Frame(topFrame)
buttonFrame = Tkinter.Frame(topFrame)
button = Tkinter.Button(top, text="build and play")
poleButton = Tkinter.Button(buttonFrame, text="add pole")
zeroButton = Tkinter.Button(buttonFrame, text="add zero")
loadButton = Tkinter.Button(top, text="load sound")

# GUI element class to display an entry in the root list (right side of interface)

class RootListEntry(Tkinter.Frame):
    def __init__(self, parent=None):
        Tkinter.Frame.__init__(self, parent)

        self.label = Tkinter.Label(self, width=16, bg="white", relief=Tkinter.GROOVE, pady=4)
        self.pairButton = Tkinter.Button(self, text="Pair")
        self.removeButton = Tkinter.Button(self, text="Remove")

        self.label.grid(row=0, column=0)
        self.pairButton.grid(row=0, column=1)
        self.removeButton.grid(row=0, column=2)

zPlaneComplex = ComplexCanvas(zPlane, -2+2j, 4+4j)

log20 = cmath.log(2.0)
log02 = cmath.log(0.2)
pi = cmath.pi

sPlaneComplex = ComplexCanvas(sPlane, log02 + 3.25j, (log20 - log02) + 6.5j)

'''
# draw sound wave
canvas.create_line(0.0, 256.0, 512.0, 256.0)
widthCompressionFactor = 512.0 / len(normalizedSoundFloats)

for sampleIndex in range(1, len(normalizedSoundFloats)):
    xA = (sampleIndex - 1) * widthCompressionFactor
    yA = 256.0 - 128.0 * normalizedSoundFloats[sampleIndex - 1]
    xB = sampleIndex * widthCompressionFactor
    yB = 256.0 - 128.0 * normalizedSoundFloats[sampleIndex]
    canvas.create_line(xA, yA, xB, yB)
'''

class EntryElements:
    def __init__(self, zPlaneDrawable, sPlaneDrawable, complexRoot):
        self.zPlaneDrawable = zPlaneDrawable
        self.sPlaneDrawable = sPlaneDrawable
        self.complexRoot = complexRoot

entryDictionary = {}
activeEntry = None

def makeActive(entry):
    global activeEntry

    if (activeEntry != None):
        key = id(activeEntry)
        entryDictionary[key].zPlaneDrawable.setColor("black")
        entryDictionary[key].sPlaneDrawable.setColor("black")
        activeEntry.label.config(bg="white")

    activeEntry = entry

    key = id(activeEntry)
    entryDictionary[key].zPlaneDrawable.setColor("green")
    entryDictionary[key].sPlaneDrawable.setColor("green")
    activeEntry.label.config(bg="green")

def setActivePosition(position):
    key = id(activeEntry)
    entryDictionary[key].complexRoot.setPosition(position)
    return entryDictionary[key].complexRoot.getPosition()

def entryClick(event):
    makeActive(event.widget._nametowidget(event.widget.winfo_parent()))

def updatePosition(position):
    position = round(position.real, 5) + round(position.imag, 5) * 1j
    position = setActivePosition(position)

    zPlanePoint = position
    sPlanePoint = cmath.log(position)

    key = id(activeEntry)
    entryDictionary[key].zPlaneDrawable.setPosition(zPlanePoint)
    entryDictionary[key].sPlaneDrawable.setPosition(sPlanePoint)

    activeEntry.label.config(text=repr(position))

def entryRightClick(event):
    key = id(event.widget._nametowidget(event.widget.winfo_parent()))
    if (entryDictionary[key].complexRoot.pair == True):
        entryDictionary[key].complexRoot.pair = False
    else:
        entryDictionary[key].complexRoot.pair = True
    updatePosition(entryDictionary[key].complexRoot.getPosition())

# create Z-plane graph of three circles and a real axis

unitCircle = zPlaneComplex.addOvalItem(-1-1j, 1+1j, outline="black")
maximumCircle = zPlaneComplex.addOvalItem(-2-2j, 2+2j, outline="blue")
minimumCircle = zPlaneComplex.addOvalItem(-0.2-0.2j, 0.2+0.2j, outline="red")
realAxis = zPlaneComplex.addLineItem(-2.0, 2.0, stipple="gray75")

# create S-plane graph of three radius lines and three real axis lines

unitLine = sPlaneComplex.addLineItem(0 + pi*1j, 0 - pi*1j, fill="black")
maximumLine = sPlaneComplex.addLineItem(log20 + pi*1j, log20 - pi*1j, fill="blue")
minimumLine = sPlaneComplex.addLineItem(log02 + pi*1j, log02 - pi*1j, fill="red")
realAxisZero = sPlaneComplex.addLineItem(log02, log20, stipple="gray75")
realAxisPositivePi = sPlaneComplex.addLineItem(log02 + pi*1j, log20 + pi*1j, stipple="gray75")
realAxisNegativePi = sPlaneComplex.addLineItem(log02 - pi*1j, log20 - pi*1j, stipple="gray75")

def removeActiveEntry():
    global activeEntry

    key = id(activeEntry)

    entryDictionary[key].zPlaneDrawable.remove()
    entryDictionary[key].sPlaneDrawable.remove()
    del entryDictionary[key]

    activeEntry.destroy()
    activeEntry = None

def entryRemove(event):
    makeActive(event.widget._nametowidget(event.widget.winfo_parent()))
    removeActiveEntry()

def addNewEntry(position, isZero):
    entry = RootListEntry(frame)
    entry.label.bind("<Button-1>", entryClick)
    entry.pairButton.bind("<Button-1>", entryRightClick)
    entry.removeButton.bind("<Button-1>", entryRemove)

    for entryIndex in range(0, len(frame.winfo_children())):
        frame.winfo_children()[entryIndex].grid(row = entryIndex)

    key = id(entry)

    if (isZero):
        entryRoot = Zero(position)
        zPlaneRoot = DrawableZero(zPlaneComplex, entryRoot.getPosition())
        sPlaneRoot = DrawableZero(sPlaneComplex, cmath.log(entryRoot.getPosition()))
    else:
        entryRoot = Pole(position)
        zPlaneRoot = DrawablePole(zPlaneComplex, entryRoot.getPosition())
        sPlaneRoot = DrawablePole(sPlaneComplex, cmath.log(entryRoot.getPosition()))

    entry.label.config(text=repr(entryRoot.getPosition()))

    entryDictionary[key] = EntryElements(zPlaneRoot, sPlaneRoot, entryRoot)

addNewEntry(0.5, False)
addNewEntry(-0.5, True)

def zPlaneMouseClick(event):
    complexMouse = zPlaneComplex.inverseTransformPoint(event.x + event.y * 1j)
    updatePosition(complexMouse)

def sPlaneMouseClick(event):
    complexMouse = sPlaneComplex.inverseTransformPoint(event.x + event.y * 1j)
    updatePosition(cmath.exp(complexMouse))

def rclick(event):
    removeActiveEntry()

def addPole():
    addNewEntry(0.5, False)

def addZero():
    addNewEntry(0.5, True)

def loadSound():
    global inputSound
    global originalSamples

    filename = tkFileDialog.askopenfilename(filetypes=[("Waveform Audio", ".wav")])
    inputSound = loadSoundFromFile(filename)
    originalSamples = inputSound.sampleFloats

# method to create filter based on current configuration and play filtered sound

def buttonClick():
    Zero.list = []
    Pole.list = []

    for key in entryDictionary.keys():
        entryDictionary[key].complexRoot.addToList()

    soundFilter = Filter(Zero.list, Pole.list)
    filteredSamples = soundFilter.filterStream(originalSamples)

    inputSound.sampleFloats = filteredSamples
    snd.play(getWaveBytes(inputSound))

zPlane.bind("<Button-1>", zPlaneMouseClick)
#zPlane.bind("<Motion>", zPlaneMouseClick)
sPlane.bind("<Button-1>", sPlaneMouseClick)

zPlane.grid(row=0, column=0)
sPlane.grid(row=0, column=1)
topFrame.grid(row=0, column=2)
frame.grid(row=0, column=0)
buttonFrame.grid(row=1, column=0)
button.grid(row=1, column=1)
button.config(command = buttonClick)
poleButton.grid(row=0, column=0)
zeroButton.grid(row=0, column=1)
poleButton.config(command = addPole)
zeroButton.config(command = addZero)
loadButton.grid(row=1, column=0)
loadButton.config(command = loadSound)

top.mainloop()
