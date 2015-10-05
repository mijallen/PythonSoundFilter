# wrapper class for a Tkinter canvas with transforms based on complex numbers

'''
Scale is determined by (canvasWidth-1) divided by domain of the graph
Offset is simply the upper-left corner coordinate of the graph domain
Padding is to compensate for the fact that canvas coordinates are offset by 2 pixels
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

# independent canvas element classes that keep a reference to the canvas

class DrawableRoot:
    def __init__(self, complexCanvas, position = 0.5, pair = False):
        self.complexCanvas = complexCanvas

class DrawableZero(DrawableRoot):
    def __init__(self, complexCanvas, position = 0.5, pair = False):
        DrawableRoot.__init__(self, complexCanvas, position, pair)
        self.ovalA = self.complexCanvas.addOvalItem(0+0j, 0+0j)
        self.ovalB = self.complexCanvas.addOvalItem(0+0j, 0+0j)
        self.setPosition(position)

    def setPosition(self, position):
        self.complexCanvas.setItemPositionScreenSpace(self.ovalA, position, 5+5j)
        self.complexCanvas.setItemPositionScreenSpace(self.ovalB, position.conjugate(), 5+5j)

    def remove(self):
        self.complexCanvas.deleteItem(self.ovalA)
        self.complexCanvas.deleteItem(self.ovalB)

    def setColor(self, color):
        self.complexCanvas.configureItem(self.ovalA, outline=color)
        self.complexCanvas.configureItem(self.ovalB, outline=color)

class DrawablePole(DrawableRoot):
    def __init__(self, complexCanvas, position = 0.5, pair = False):
        DrawableRoot.__init__(self, complexCanvas, position, pair)
        self.lineA = self.complexCanvas.addLineItem(0+0j, 0+0j)
        self.lineB = self.complexCanvas.addLineItem(0+0j, 0+0j)
        self.lineC = self.complexCanvas.addLineItem(0+0j, 0+0j)
        self.lineD = self.complexCanvas.addLineItem(0+0j, 0+0j)
        self.setPosition(position)

    def setPosition(self, position):
        self.complexCanvas.setItemPositionScreenSpace(self.lineA, position, 5+5j)
        self.complexCanvas.setItemPositionScreenSpace(self.lineB, position, 5-5j)
        self.complexCanvas.setItemPositionScreenSpace(self.lineC, position.conjugate(), 5+5j)
        self.complexCanvas.setItemPositionScreenSpace(self.lineD, position.conjugate(), 5-5j)

    def remove(self):
        self.complexCanvas.deleteItem(self.lineA)
        self.complexCanvas.deleteItem(self.lineB)
        self.complexCanvas.deleteItem(self.lineC)
        self.complexCanvas.deleteItem(self.lineD)

    def setColor(self, color):
        self.complexCanvas.configureItem(self.lineA, fill=color)
        self.complexCanvas.configureItem(self.lineB, fill=color)
        self.complexCanvas.configureItem(self.lineC, fill=color)
        self.complexCanvas.configureItem(self.lineD, fill=color)
