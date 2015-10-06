#!/usr/bin/python

import Tkinter, tkFileDialog, tkMessageBox
import cmath
import pymedia.audio.sound as sound

from Sound import *
from Filter import *
from ComplexRoot import *
from Drawable import *

inputSoundInfo, originalSamples = loadSoundFromFile('static.wav')

format = sound.AFMT_S16_LE
snd = sound.Output(inputSoundInfo.sampleRate, inputSoundInfo.channelCount, format)

'''
Possible Additions:
 -graph frequency response by finding magnitude of various points in z- or s- plane
   -use cubic or cosine interpolation, include pole/zero angles in the sample points
 -sliding window for graphing of audio wave forms
 -ability to generate sounds (statics, waves, drum beats)
'''

'''
# possible code for drawing a sound wave
canvas.create_line(0.0, 256.0, 512.0, 256.0)
widthCompressionFactor = 512.0 / len(normalizedSoundFloats)

for sampleIndex in range(1, len(normalizedSoundFloats)):
    xA = (sampleIndex - 1) * widthCompressionFactor
    yA = 256.0 - 128.0 * normalizedSoundFloats[sampleIndex - 1]
    xB = sampleIndex * widthCompressionFactor
    yB = 256.0 - 128.0 * normalizedSoundFloats[sampleIndex]
    canvas.create_line(xA, yA, xB, yB)
'''

#when zero placed around 1 and pole pair placed around +/-i, sounds like clipping


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

# class to organize related items into a dictionary entry

class EntryElements:
    def __init__(self, zPlaneDrawable, sPlaneDrawable, complexRoot):
        self.zPlaneDrawable = zPlaneDrawable
        self.sPlaneDrawable = sPlaneDrawable
        self.complexRoot = complexRoot

# define some constants

canvasWidth = 400
canvasHeight = 400

log20 = cmath.log(2.0)
log02 = cmath.log(0.2)
pi = cmath.pi

# create new GUI context

top = Tkinter.Tk()

# add a canvas to represent the complex Z-plane

zPlane = Tkinter.Canvas(top, bg="white", width=canvasWidth, height=canvasHeight)
zPlane.grid(row=0, column=0)
zPlaneComplex = ComplexCanvas(zPlane, -2+2j, 4+4j)

# create Z-plane graph of three circles and a real axis

unitCircle = zPlaneComplex.addOvalItem(-1-1j, 1+1j, outline="black")
maximumCircle = zPlaneComplex.addOvalItem(-2-2j, 2+2j, outline="blue")
minimumCircle = zPlaneComplex.addOvalItem(-0.2-0.2j, 0.2+0.2j, outline="red")
realAxis = zPlaneComplex.addLineItem(-2.0, 2.0, stipple="gray75")

# add a canvas to represent the complex S-plane

sPlane = Tkinter.Canvas(top, bg="white", width=canvasWidth, height=canvasHeight)
sPlane.grid(row=0, column=1)
sPlaneComplex = ComplexCanvas(sPlane, log02 + 3.25j, (log20 - log02) + 6.5j)

# create S-plane graph of three radius lines and three real axis lines

unitLine = sPlaneComplex.addLineItem(0 + pi*1j, 0 - pi*1j, fill="black")
maximumLine = sPlaneComplex.addLineItem(log20 + pi*1j, log20 - pi*1j, fill="blue")
minimumLine = sPlaneComplex.addLineItem(log02 + pi*1j, log02 - pi*1j, fill="red")
realAxisZero = sPlaneComplex.addLineItem(log02, log20, stipple="gray75")
realAxisPositivePi = sPlaneComplex.addLineItem(log02 + pi*1j, log20 + pi*1j, stipple="gray75")
realAxisNegativePi = sPlaneComplex.addLineItem(log02 - pi*1j, log20 - pi*1j, stipple="gray75")

# create the entry list GUI based on a frame hierarchy

entryListFrame = Tkinter.Frame(top)
entryListFrame.grid(row=0, column=2)

entryFrame = Tkinter.Frame(entryListFrame)
entryFrame.grid(row=0, column=0)

addButtonsFrame = Tkinter.Frame(entryListFrame)
addButtonsFrame.grid(row=1, column=0)

# create buttons to add a pole or zero

addPoleButton = Tkinter.Button(addButtonsFrame, text="add pole")
addPoleButton.grid(row=0, column=0)

addZeroButton = Tkinter.Button(addButtonsFrame, text="add zero")
addZeroButton.grid(row=0, column=1)

# create load and save sound buttons

fileButtonFrame = Tkinter.Frame(top)
fileButtonFrame.grid(row=1, column=0)

loadSoundButton = Tkinter.Button(fileButtonFrame, text="load sound")
loadSoundButton.grid(row=0, column=0)

saveSoundButton = Tkinter.Button(fileButtonFrame, text="save sound")
saveSoundButton.grid(row=0, column=1)

# create play buttons for filtered and original sound

playButtonFrame = Tkinter.Frame(top)
playButtonFrame.grid(row=1, column=1)

playOriginalSoundButton = Tkinter.Button(playButtonFrame, text="play original")
playOriginalSoundButton.grid(row=0, column=0)

playFilteredSoundButton = Tkinter.Button(playButtonFrame, text="play filtered")
playFilteredSoundButton.grid(row=0, column=1)

# create show coefficients button

showCoefficientsButton = Tkinter.Button(top, text="show coeffients")
showCoefficientsButton.grid(row=1, column=2)

# declare a global entry dictionary and a specified 'active' entry

entryDictionary = {}
activeEntry = None

# functions to modify existing entries

def makeEntryActive(entry):
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

def updateEntryPosition(entry, position):
    position = round(position.real, 5) + round(position.imag, 5) * 1j

    key = id(entry)
    entryDictionary[key].complexRoot.setPosition(position)
    position = entryDictionary[key].complexRoot.getPosition()

    zPlanePoint = position
    sPlanePoint = cmath.log(position)

    entryDictionary[key].zPlaneDrawable.setPosition(zPlanePoint)
    entryDictionary[key].sPlaneDrawable.setPosition(sPlanePoint)

    entry.label.config(text=repr(position))

def removeEntry(entry):
    global activeEntry

    key = id(entry)

    if (key == id(activeEntry)):
        activeEntry = None

    entryDictionary[key].zPlaneDrawable.remove()
    entryDictionary[key].sPlaneDrawable.remove()
    del entryDictionary[key]

    entry.destroy()

# functions called when a GUI element of an entry is clicked

def entrySelect(event):
    entry = event.widget._nametowidget(event.widget.winfo_parent())
    makeEntryActive(entry)

def entryPair(event):
    entry = event.widget._nametowidget(event.widget.winfo_parent())
    key = id(entry)
    if (entryDictionary[key].complexRoot.pair == True):
        entryDictionary[key].complexRoot.pair = False
    else:
        entryDictionary[key].complexRoot.pair = True
    updateEntryPosition(entry, entryDictionary[key].complexRoot.getPosition())

def entryRemove(event):
    entry = event.widget._nametowidget(event.widget.winfo_parent())
    removeEntry(entry)

# function to create a new entry

def addNewEntry(position, isZero):
    entry = RootListEntry(entryFrame)
    entry.label.bind("<Button-1>", entrySelect)
    entry.pairButton.bind("<Button-1>", entryPair)
    entry.removeButton.bind("<Button-1>", entryRemove)

   # organize existing list of entries
    for entryIndex in range(0, len(entryFrame.winfo_children())):
        entryFrame.winfo_children()[entryIndex].grid(row = entryIndex)

    if (isZero):
        entryRoot = Zero(position)
        zPlaneRoot = DrawableZero(zPlaneComplex, entryRoot.getPosition())
        sPlaneRoot = DrawableZero(sPlaneComplex, cmath.log(entryRoot.getPosition()))
    else:
        entryRoot = Pole(position)
        zPlaneRoot = DrawablePole(zPlaneComplex, entryRoot.getPosition())
        sPlaneRoot = DrawablePole(sPlaneComplex, cmath.log(entryRoot.getPosition()))

    entry.label.config(text=repr(entryRoot.getPosition()))

    key = id(entry)
    entryDictionary[key] = EntryElements(zPlaneRoot, sPlaneRoot, entryRoot)

# function to move active root based on clicking z-plane

def zPlaneMouseClick(event):
    complexMouse = zPlaneComplex.inverseTransformPoint(event.x + event.y * 1j)
    if (activeEntry != None):
        updateEntryPosition(activeEntry, complexMouse)

zPlane.bind("<Button-1>", zPlaneMouseClick)
#zPlane.bind("<Motion>", zPlaneMouseClick)

# function to move active root based on clicking s-plane

def sPlaneMouseClick(event):
    complexMouse = sPlaneComplex.inverseTransformPoint(event.x + event.y * 1j)
    if (activeEntry != None):
        updateEntryPosition(activeEntry, cmath.exp(complexMouse))

sPlane.bind("<Button-1>", sPlaneMouseClick)

# function to add a new pole at 0.5 based on clicking add pole button

def addPole():
    addNewEntry(0.5, False)

addPoleButton.config(command = addPole)

# function to add a new zero at 0.5 based on clicking add zero button

def addZero():
    addNewEntry(0.5, True)

addZeroButton.config(command = addZero)

# method to load a sound based on clicking load sound button

def loadSound():
    global inputSoundInfo
    global originalSamples

    filename = tkFileDialog.askopenfilename(filetypes=[("Waveform Audio", ".wav")])
    inputSoundInfo, originalSamples = loadSoundFromFile(filename)

loadSoundButton.config(command = loadSound)

# method to save a filtered sound based on a button press

def saveSound():
    Zero.list = []
    Pole.list = []

    for key in entryDictionary.keys():
        entryDictionary[key].complexRoot.addToList()

    soundFilter = Filter(Zero.list, Pole.list)
    filteredSamples = soundFilter.filterStream(originalSamples)

    filename = tkFileDialog.asksaveasfilename(filetypes=[("Waveform Audio", ".wav")],
        defaultextension='.wav')
    saveSoundToFile(inputSoundInfo, filteredSamples, filename)

saveSoundButton.config(command = saveSound)

# method to play original sound based on a button press

def playOriginalSound():
    snd.play(getWaveBytes(inputSoundInfo, originalSamples))

playOriginalSoundButton.config(command = playOriginalSound)

# method to create filter based on current configuration and play filtered sound

def playFilteredSound():
    Zero.list = []
    Pole.list = []

    for key in entryDictionary.keys():
        entryDictionary[key].complexRoot.addToList()

    soundFilter = Filter(Zero.list, Pole.list)
    filteredSamples = soundFilter.filterStream(originalSamples)

    snd.play(getWaveBytes(inputSoundInfo, filteredSamples))

playFilteredSoundButton.config(command = playFilteredSound)

# method to show how to build the given filter

def showCoefficients():
    Zero.list = []
    Pole.list = []

    for key in entryDictionary.keys():
        entryDictionary[key].complexRoot.addToList()

    soundFilter = Filter(Zero.list, Pole.list)

    message = "y[n] = " + repr(round(soundFilter.scaleFactor, 5)) + " * ("

    for index, coefficient in enumerate(soundFilter.zeroCoefficients):
        message += repr(round(coefficient.real, 5)) + " * x[n-" + repr(index) + "] + "

    message = message[0:len(message)-3] + ") + "

    poleCoefficientCount = len(soundFilter.poleCoefficients)

    for index, coefficient in enumerate(soundFilter.poleCoefficients[1:poleCoefficientCount]):
        message += repr(round(coefficient.real, 5)) + " * y[n-" + repr(index+1) + "] + "

    message = message[0:len(message)-3]

    tkMessageBox.showinfo("Filter Configuration", message)

showCoefficientsButton.config(command = showCoefficients)

# provide an initial configuration and start the main loop

addNewEntry(0.5, False)
addNewEntry(-0.5, True)

top.mainloop()
