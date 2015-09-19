#!/usr/bin/python

import Tkinter, tkFileDialog
import cmath
import pymedia.audio.sound as sound
from Sound import *
from Filter import *

inputSound = loadSoundFromFile('static.wav')

zeroList = []
zeroList.append(-0.25 + 0.1j)
zeroList.append(-0.25 - 0.1j)
zeroList.append(0.5 + 0.j)

poleList = []
poleList.append(-0.5j)
poleList.append(0.5j)

testFilter = Filter(zeroList, poleList)
filteredSamples = testFilter.filterStream(inputSound.sampleFloats)

inputSound.sampleFloats = filteredSamples
#saveSoundToFile(inputSound, 'out.wav')

format = sound.AFMT_S16_LE
snd = sound.Output(inputSound.sampleRate, inputSound.channelCount, format)
snd.play(getWaveBytes(inputSound))

normalizedSoundFloats = filteredSamples

top = Tkinter.Tk()

'''
Proposed Design:
 -(DECLINED) use non-linear radius expansion for z-plane graph (radius squared?)
 -(DECLINED) graph s-plane from x of -c to c so that z-plane has radius from exp(-c) to exp(c)
 -graph frequency response by finding magnitude of various points in z- or s- plane
   -use cubic or cosine interpolation, include pole/zero angles in the sample points
 -(in progress) have ability to add single real point or a conjugate pair
 -(in progress) restrict poles to within unit circle for z-plane and negative half for s-plane
 -add buttons to play original audio and new, filtered audio
 -maybe use file dialog boxes for loading/saving WAV files?
 -maybe use sliding window for graphing of audio wave forms?
 -maybe have ability to generate sounds (statics, waves, drum beats)?
 -maybe an 'apply filter' button?
 -should sound info be its own class and the float array be separate?
'''

# Base class for roots of the complex transfer function (roots of numerator or denominator)

class Root:
    def __init__(self):
        raise NotImplementedError("cannot instantiate abstract class Root")

    def addToList(self):
        if (self.pair):
            self.putInSpecifiedList(self.position)
            self.putInSpecifiedList(self.position.conjugate())
        else:
            self.putInSpecifiedList(self.position)

    def putInSpecifiedList(self):
        raise NotImplementedError("cannot call abstract method putInSpecifiedList from Root class")

    def setPosition(self, position):
        self.position = position
        if (self.pair == False):
            self.position = self.position.real
        self.restrictPosition()

    def getPosition(self):
        return self.position

    def restrictPosition(self):
        raise NotImplementedError("cannot call abstract method restrictPosition from Root class")

# inheriting Zero class has its own list, not restricted within unit circle
# still need to make pair and position "private" variables, add getter/setter for pair

class Zero(Root):
    list = []
    minimumRadius = 0.2
    maximumRadius = 2.0

    def __init__(self, position):
        self.pair = False
        self.setPosition(position)

    def putInSpecifiedList(self, position):
        Zero.list.append(position)

    def restrictPosition(self):
        length = abs(self.position)
        if (length < Zero.minimumRadius):
            self.position *= Zero.minimumRadius / length
        if (length > Zero.maximumRadius):
            self.position *= Zero.maximumRadius / length

# inherting Pole class has its own list, must stay within unit circle

class Pole(Root):
    list = []
    minimumRadius = 0.2
    maximumRadius = 1.0

    def __init__(self, position):
        self.pair = False
        self.setPosition(position)

    def putInSpecifiedList(self, position):
        Pole.list.append(position)

    def restrictPosition(self):
        length = abs(self.position)
        if (length < Pole.minimumRadius):
            self.position *= Pole.minimumRadius / length
        if (length > Pole.maximumRadius):
            self.position *= Pole.maximumRadius / length

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
frame = Tkinter.Frame(top, width=canvasWidth, height=canvasHeight)

'''
Scale is determined by (canvasWidth-1) divided by domain of the graph
Offset is simply the upper-left corner coordinate of the graph domain
Padding is to compensate for the fact that canvas coordinates are offset by 2 pixels

Need a class to represent roots as canvas elements
will probably be self-sufficient (have reference to ComplexCanvas)
Thinking of having a base RootCanvasItem with inheriting ZeroCanvasItem, PoleCanvasItem
ZeroCanvasItem will have two ovals (one might not be used) it must update
PoleCanvasItem will have four lines (two might not be used, two per X)
each dictionary entry will have 2 ZeroCanvasItems and a Zero (or PoleCanvasItems, Pole)
'''

class ComplexCanvas:
    def __init__(self, canvas, topLeftComplex, dimensionsComplex, paddingComplex = 2 + 2j):
        self.canvas = canvas
        self.offset = -topLeftComplex
        canvasWidth = canvas.winfo_reqwidth() - 2 * paddingComplex.real
        canvasHeight = canvas.winfo_reqheight() - 2 * paddingComplex.imag
        self.scale = (canvasWidth - 1.0) / dimensionsComplex.real
        self.scale -= (canvasHeight - 1.0) / dimensionsComplex.imag * 1j
        self.padding = paddingComplex

    def transformPoint(self, complexPoint):
        canvasPoint = (complexPoint.real + self.offset.real) * self.scale.real
        canvasPoint += (complexPoint.imag + self.offset.imag) * self.scale.imag * 1j
        canvasPoint += self.padding
        return canvasPoint

    def inverseTransformPoint(self, canvasPoint):
        canvasPoint -= self.padding
        complexPoint = canvasPoint.real / self.scale.real - self.offset.real
        complexPoint += (canvasPoint.imag / self.scale.imag - self.offset.imag) * 1j
        return complexPoint

    def addOvalItem(self, complexPointA, complexPointB, **options):
        oval = self.canvas.create_oval(0, 0, 0, 0, options)
        self.setItemPosition(oval, complexPointA, complexPointB)
        return oval

    def addLineItem(self, complexPointA, complexPointB, **options):
        line = self.canvas.create_line(0, 0, 0, 0, options)
        self.setItemPosition(line, complexPointA, complexPointB)
        return line

    def setItemPosition(self, item, complexPointA, complexPointB):
        canvasPointA = self.transformPoint(complexPointA)
        canvasPointB = self.transformPoint(complexPointB)
        self.canvas.coords(item, canvasPointA.real, canvasPointA.imag,
            canvasPointB.real, canvasPointB.imag)

    def setItemPositionScreenSpace(self, item, complexPoint, scaleComplex):
        canvasPoint = self.transformPoint(complexPoint)
        self.canvas.coords(item, canvasPoint.real - scaleComplex.real,
            canvasPoint.imag - scaleComplex.imag,
            canvasPoint.real + scaleComplex.real,
            canvasPoint.imag + scaleComplex.imag)

    def configureItem(self, item, **options):
        self.canvas.itemconfigure(item, options)

    def deleteItem(self, item):
        self.canvas.delete(item)

zPlaneComplex = ComplexCanvas(zPlane, -2+2j, 4+4j)

log20 = cmath.log(2.0)
log02 = cmath.log(0.2)
pi = cmath.pi

sPlaneComplex = ComplexCanvas(sPlane, log02 + 3.25j, (log20 - log02) + 6.4j)

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

#button = Tkinter.Button(frame, text="button")

entryDictionary = {}
ZPLANEOVAL = 0
SPLANEOVAL = 1
ENTRYROOT = 2

activeEntry = None

def makeActive(entry):
    global activeEntry

    if (activeEntry != None):
        key = id(activeEntry)
        zPlaneComplex.configureItem(entryDictionary[key][ZPLANEOVAL], outline="black")
        sPlaneComplex.configureItem(entryDictionary[key][SPLANEOVAL], outline="black")
        activeEntry.config(bg="white")

    activeEntry = entry

    key = id(activeEntry)
    zPlaneComplex.configureItem(entryDictionary[key][ZPLANEOVAL], outline="green")
    sPlaneComplex.configureItem(entryDictionary[key][SPLANEOVAL], outline="green")
    activeEntry.config(bg="green")

def setActivePosition(position):
    key = id(activeEntry)
    entryDictionary[key][ENTRYROOT].setPosition(position)
    return entryDictionary[key][ENTRYROOT].getPosition()

def entryClick(event):
    makeActive(event.widget)

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

def addNewEntry(position, isZero):
    entry = Tkinter.Entry(frame)
    #entry.grid(row = len(entryDictionary))
    entry.bind("<Button-1>", entryClick)

    for entryIndex in range(0, len(frame.winfo_children())):
        frame.winfo_children()[entryIndex].grid(row = entryIndex)

    key = id(entry)

    if (isZero):
        entryRoot = Zero(position)
    else:
        entryRoot = Pole(position)

    zPlaneOval = zPlaneComplex.addOvalItem(0,0)
    zPlaneComplex.setItemPositionScreenSpace(zPlaneOval, entryRoot.getPosition(), 5+5j)

    sPlaneOval = sPlaneComplex.addOvalItem(0,0)
    sPlaneComplex.setItemPositionScreenSpace(sPlaneOval, cmath.log(entryRoot.getPosition()), 5+5j)

    entryDictionary[key] = (zPlaneOval, sPlaneOval, entryRoot)

def removeActiveEntry():
    global activeEntry

    key = id(activeEntry)

    zPlaneComplex.deleteItem(entryDictionary[key][ZPLANEOVAL])
    sPlaneComplex.deleteItem(entryDictionary[key][SPLANEOVAL])
    del entryDictionary[key]

    activeEntry.destroy()
    activeEntry = None

for index in range(0, len(zeroList)):
    addNewEntry(zeroList[index], True)

addNewEntry(0.5, False)
#makeActive(entryList[0])

def updatePosition(position):
    position = round(position.real, 5) + round(position.imag, 5) * 1j
    position = setActivePosition(position)

    zPlanePoint = position
    sPlanePoint = cmath.log(position)

    print zPlanePoint

    key = id(activeEntry)
    zPlaneComplex.setItemPositionScreenSpace(entryDictionary[key][ZPLANEOVAL], zPlanePoint, 5+5j)
    sPlaneComplex.setItemPositionScreenSpace(entryDictionary[key][SPLANEOVAL], sPlanePoint, 5+5j)

    print zPlane.coords(entryDictionary[key][ZPLANEOVAL])

    activeEntry.delete(0, Tkinter.END)
    activeEntry.insert(0, repr(position))

def zPlaneMouseClick(event):
    complexMouse = zPlaneComplex.inverseTransformPoint(event.x + event.y * 1j)
    updatePosition(complexMouse)

def sPlaneMouseClick(event):
    complexMouse = sPlaneComplex.inverseTransformPoint(event.x + event.y * 1j)
    updatePosition(cmath.exp(complexMouse))

def rclick(event):
    removeActiveEntry()
    print frame.winfo_children()

def mclick(event):
    addNewEntry(0.5, True)
    print frame.winfo_children()

zPlane.bind("<Button-1>", zPlaneMouseClick)
#zPlane.bind("<Motion>", zPlaneMouseClick)
sPlane.bind("<Button-1>", sPlaneMouseClick)

zPlane.bind("<Button-2>", mclick)
zPlane.bind("<Button-3>", rclick)

zPlane.grid(row=0, column=0)
sPlane.grid(row=0, column=1)
frame.grid(row=0, column=2)
#button.grid(row=0, column=0)

#filename = tkFileDialog.askopenfilename()

top.mainloop()
