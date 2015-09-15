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
        zPlane.itemconfig(entryDictionary[key][ZPLANEOVAL], outline="black")
        sPlane.itemconfig(entryDictionary[key][SPLANEOVAL], outline="black")
        activeEntry.config(bg="white")

    activeEntry = entry

    key = id(activeEntry)
    zPlane.itemconfig(entryDictionary[key][ZPLANEOVAL], outline="green")
    sPlane.itemconfig(entryDictionary[key][SPLANEOVAL], outline="green")
    activeEntry.config(bg="green")

def setActivePosition(position):
    key = id(activeEntry)
    entryDictionary[key][ENTRYROOT].setPosition(position)
    return entryDictionary[key][ENTRYROOT].getPosition()

def entryClick(event):
    makeActive(event.widget)

# not needed?

#entryList = []
#for index in range(0, len(zeroList)):
#    entry = Tkinter.Entry(frame)
#    entryList.append(entry)
#    entry.grid(row = index)
#    entry.bind("<Button-1>", entryClick)

diagonal = 1.0 + 1.0j

'''
Scale is determined by (canvasWidth-1) divided by domain of the graph
Offset is simply the upper-left corner coordinate of the graph domain
Padding is to compensate for the fact that canvas coordinates are offset by 2 pixels
'''

# can probably be used for a class that contains a canvas, abstracts away transforms

canvas1Scale = (canvasWidth - 1.0) / 4.0 - (canvasWidth - 1.0) / 4.0 * 1j
canvas1Offset = -2.0 + 2.0j
canvas1Padding = 2.0 * diagonal

def canvas1InverseTransform(canvasPoint):
    canvasPoint -= canvas1Padding
    complexPoint = canvasPoint.real / canvas1Scale.real + canvas1Offset.real
    complexPoint += (canvasPoint.imag / canvas1Scale.imag + canvas1Offset.imag) * 1j
    return complexPoint

def canvas1Transform(complexPoint):
    canvasPoint = (complexPoint.real - canvas1Offset.real) * canvas1Scale.real
    canvasPoint += ( (complexPoint.imag - canvas1Offset.imag) * canvas1Scale.imag ) * 1j
    canvasPoint += canvas1Padding
    return canvasPoint

def getCanvas1BoundingBoxCoords(complexA, complexB):
    canvasPointA = canvas1Transform(complexA)
    canvasPointB = canvas1Transform(complexB)
    return canvasPointA.real, canvasPointA.imag, canvasPointB.real, canvasPointB.imag

# modified to better show negative reals from Z-plane at top of S-plane graph

canvas2Scale = (canvasWidth - 1.0) / (cmath.log(2.0) - cmath.log(0.2))
#canvas2Scale -= (canvasHeight - 1.0) / (2.0 * cmath.pi) * 1j
canvas2Scale -= (canvasHeight - 1.0) / 6.4 * 1j
#canvas2Offset = cmath.log(0.2) + cmath.pi * 1j
canvas2Offset = cmath.log(0.2) + 3.25 * 1j
canvas2Padding = 2.0 * diagonal

def canvas2Transform(complexPoint):
    canvasPoint = (complexPoint.real - canvas2Offset.real) * canvas2Scale.real
    canvasPoint += ( (complexPoint.imag - canvas2Offset.imag) * canvas2Scale.imag ) * 1j
    canvasPoint += canvas2Padding
    return canvasPoint

def canvas2InverseTransform(canvasPoint):
    canvasPoint -= canvas2Padding
    complexPoint = canvasPoint.real / canvas2Scale.real + canvas2Offset.real
    complexPoint += (canvasPoint.imag / canvas2Scale.imag + canvas2Offset.imag) * 1j
    return complexPoint

def getCanvas2BoundingBoxCoords(complexA, complexB):
    canvasPointA = canvas2Transform(complexA)
    canvasPointB = canvas2Transform(complexB)
    return canvasPointA.real, canvasPointA.imag, canvasPointB.real, canvasPointB.imag

# create Z-plane graph of three circles and a real axis

unitCircleCoords = getCanvas1BoundingBoxCoords( 1.0 * -diagonal, 1.0 * diagonal )
maximumCircleCoords = getCanvas1BoundingBoxCoords( 2.0 * -diagonal, 2.0 * diagonal )
minimumCircleCoords = getCanvas1BoundingBoxCoords( 0.2 * -diagonal, 0.2 * diagonal )
realAxisCoords = getCanvas1BoundingBoxCoords( -2.0, +2.0 )

unitCircle = zPlane.create_oval(unitCircleCoords, fill=None)
maximumCircle = zPlane.create_oval(maximumCircleCoords, fill=None, outline="blue")
minimumCircle = zPlane.create_oval(minimumCircleCoords, fill=None, outline="red")
realAxis = zPlane.create_line(realAxisCoords, stipple="gray75")

# create S-plane graph of three radius lines and three real axis lines

log20 = cmath.log(2.0)
log02 = cmath.log(0.2)

unitLineCoords = getCanvas2BoundingBoxCoords( +cmath.pi * 1.0j, -cmath.pi * 1.0j )
maximumLineCoords = getCanvas2BoundingBoxCoords( log20 + cmath.pi * 1.0j, log20 - cmath.pi * 1.0j )
minimumLineCoords = getCanvas2BoundingBoxCoords( log02 + cmath.pi * 1.0j, log02 - cmath.pi * 1.0j )

realAxisZeroCoords = getCanvas2BoundingBoxCoords( log02, log20 )
realAxisPositivePiCoords = getCanvas2BoundingBoxCoords( log02 + cmath.pi * 1j, log20 + cmath.pi * 1j )
realAxisNegativePiCoords = getCanvas2BoundingBoxCoords( log02 - cmath.pi * 1j, log20 - cmath.pi * 1j )

unitLine = sPlane.create_line(unitLineCoords)
maximumLine = sPlane.create_line(maximumLineCoords, fill="blue")
minimumLine = sPlane.create_line(minimumLineCoords, fill="red")
realAxisZero = sPlane.create_line(realAxisZeroCoords, stipple="gray75")
realAxisPositivePi = sPlane.create_line(realAxisPositivePiCoords, stipple="gray75")
realAxisNegativePi = sPlane.create_line(realAxisNegativePiCoords, stipple="gray75")

def placeCanvasOval(canvas, oval, point, radius):
    canvas.coords(oval, point.real - radius, point.imag - radius, point.real + radius, point.imag + radius)

'''
currently builds collection of poles and zeros based on zeroList
click on an entry in the panel on the right to make it active
then click inside either canvas to move it
must click an entry before clicking canvas, otherwise activeEntry == None

first entry is an unpaired Zero, can move in [-2,-0.2] and [+0.2,+2]
second entry is an unpaired Pole, can move in [-1,-0.2] and [+0.2,+1]
third entry is a "paired" Pole, can move so that magnitude in [0.2,1]

still need to have two diagonal lines for Poles, rather than and oval
still need to draw the paired pole/zero's conjugate reflected across real axis
still need to implement ability to add/remove entries
'''

for index in range(0, len(zeroList)):
    entry = Tkinter.Entry(frame)
    entry.grid(row = index)
    entry.bind("<Button-1>", entryClick)

    #key = id(entryList[index])
    key = id(entry)

    if (index == 0):
        entryRoot = Zero(zeroList[index])
    else:
        entryRoot = Pole(zeroList[index])
    if (index == 2):
        entryRoot.pair = True

    zPlaneOval = zPlane.create_oval(0, 0, 0, 0, fill=None)
    zPlanePosition = canvas1Transform( entryRoot.getPosition() )
    placeCanvasOval(zPlane, zPlaneOval, zPlanePosition, 5)

    sPlaneOval = sPlane.create_oval(0, 0, 0, 0, fill=None)
    sPlanePosition = canvas2Transform( cmath.log(entryRoot.getPosition()) )
    placeCanvasOval(sPlane, sPlaneOval, sPlanePosition, 5)

    entryDictionary[key] = (zPlaneOval, sPlaneOval, entryRoot)

#makeActive(entryList[0])

def updatePosition(position):
    position = round(position.real, 5) + round(position.imag, 5) * 1j
    position = setActivePosition(position)

    canvas1Point = canvas1Transform(position)
    canvas2Point = canvas2Transform(cmath.log(position))

    key = id(activeEntry)
    placeCanvasOval(zPlane, entryDictionary[key][ZPLANEOVAL], canvas1Point, 5)
    placeCanvasOval(sPlane, entryDictionary[key][SPLANEOVAL], canvas2Point, 5)

    activeEntry.delete(0, Tkinter.END)
    activeEntry.insert(0, repr(position))

def zPlaneMouseClick(event):
    complexMouse = canvas1InverseTransform(event.x + event.y * 1j)
    updatePosition(complexMouse)

def sPlaneMouseClick(event):
    complexMouse = canvas2InverseTransform(event.x + event.y * 1j)
    updatePosition(cmath.exp(complexMouse))

zPlane.bind("<Button-1>", zPlaneMouseClick)
#zPlane.bind("<Motion>", zPlaneMouseClick)
sPlane.bind("<Button-1>", sPlaneMouseClick)

zPlane.grid(row=0, column=0)
sPlane.grid(row=0, column=1)
frame.grid(row=0, column=2)
#button.grid(row=0, column=0)

#filename = tkFileDialog.askopenfilename()

top.mainloop()
